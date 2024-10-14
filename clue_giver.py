import itertools
import numpy as np
import torch
import pickle


class ClueGiver:
    def __init__(self, model, tokenizer, good_words, bad_words, device,
                 primer="Here is a list of unique words that are related to each other: [", dataset_file="dataset.pkl"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.primer = primer
        self.remove_word_indices = []
        self.words_to_guess = good_words
        self.words_to_not_guess = bad_words
        self._add_bad_guesses()
        self._init_remove_words(good_words, bad_words)
        self.last_hint = ""
        self._dataset_file = dataset_file

    def _make_prompt(self, word_list):
        prompt = self.primer
        for word in word_list:
            prompt = f"{prompt} {word},"
        return prompt

    def _add_bad_guesses(self):
        bad_guesses = ["ich", "etc"]
        for word in bad_guesses:
            self.words_to_not_guess.append(word)

    def _init_remove_words(self, good_words, bad_words):
        biggest_good_prompt = self._make_prompt(good_words)
        biggest_bad_prompt = self._make_prompt(bad_words)
        for word in self.words_to_guess:
            bad_index = self.tokenizer(word, return_tensors="pt")["input_ids"].to(self.device)
            self.remove_word_indices.append(bad_index)
            bad_index = self.tokenizer(f" {word}", return_tensors="pt")["input_ids"].to(self.device)
            self.remove_word_indices.append(bad_index)

        good_prompt_ids = self.tokenizer(biggest_good_prompt, return_tensors="pt")["input_ids"].to(self.device)
        bad_prompt_ids = self.tokenizer(biggest_bad_prompt, return_tensors="pt")["input_ids"].to(self.device)

        for ID in good_prompt_ids:
            self.remove_word_indices.append(ID)
        for ID in bad_prompt_ids:
            self.remove_word_indices.append(ID)
        return
        #####################################

    def get_clue(self):
        scores = []
        words = []
        word_permutations = self._get_permutations()
        if len(word_permutations) == 0:
            return [], [], 0.0, [], "dog", 0
        bad_prompt = self._make_prompt(self.words_to_not_guess)
        bad_probs = self._get_probabilities(bad_prompt)

        for permutation in word_permutations:
            current_prompt = self._make_prompt(permutation)
            good_probs = self._get_probabilities(current_prompt)
            word, score, index = self._get_word_score_and_token_index(good_probs, bad_probs, current_prompt)
            scores.append(score)
            words.append((permutation, word, index))
        try:
            best_index = np.argmax(scores)
        except ValueError as e:
            print(e)
            return [], [], 0.0, self.words_to_guess[0], "dog", 0
        words_that_you_should_guess, best_clue, index = words[best_index]
        self.last_hint = best_clue.lower().strip()
        self._make_dataset(words_that_you_should_guess, best_clue)
        if len(words_that_you_should_guess) == 0:
            raise Exception("What the hell")
        return scores, words, scores[best_index], words_that_you_should_guess, best_clue, index

    def _get_word_score_and_token_index(self, good_probs, bad_probs, prompt):
        diff = good_probs - bad_probs
        diff_no_repeats = self._remove_repeats(diff)
        diff_no_bad_clues, word = self._make_sure_good_clue(diff_no_repeats, prompt)
        score = diff_no_repeats[torch.argmax(diff_no_bad_clues)].item()
        index = torch.argmax(diff_no_bad_clues)
        return word, score, index

    def _make_sure_good_clue(self, probs, prompt):
        clue = self._generate_until_done_with_word(self.tokenizer.decode(torch.argmax(probs)), prompt)

        while self._clue_bad(clue):
            probs[torch.argmax(probs)] = -1
            clue = self._generate_until_done_with_word(self.tokenizer.decode(torch.argmax(probs)), prompt)
        return probs, clue
        #####################################

    def _clue_bad(self, clue):
        if not all(i.isalpha() for i in clue.strip()):          # Has numbers = bad clue
            return True
        if clue.lower().strip() in self.words_to_guess:         # is one of the words on the board = bad clue
            return True
        if clue.lower().strip() == self.last_hint.lower().strip():  # same hint as last time = not human play style
            return True
        if len(clue.lower().strip()) <= 2:                      # too short
            return True

        for word in self.words_to_guess:                        # subword of words to guess = cheating
            if clue.lower().strip() in word.lower().strip():
                return True
            if word.lower().strip() in clue.lower().strip():
                return True

        for word in self.words_to_not_guess:                    # subword of words to not guess = stupid
            if clue.lower().strip() in word.lower().strip():
                return True
            if word.lower().strip() in clue.lower().strip():
                return True
        return False

    def _remove_repeats(self, probs):
        for ID in self.remove_word_indices:
            probs[ID] = -1
        return probs
        #####################################

    def _get_probabilities(self, prompt):
        input_ids = self.tokenizer(prompt, return_tensors="pt")["input_ids"].to(self.device)
        with torch.no_grad():
            output = self.model(input_ids=input_ids)
            logits = output.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1)
        return probs

    def _generate_until_done_with_word(self, word, prompt):
        og_word = word
        input_ids = self.tokenizer(f"{prompt}{word}", return_tensors="pt")["input_ids"].to(self.device)
        with torch.no_grad():
            output = self.model(input_ids=input_ids)
            logits = output.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1)
            next_word = self.tokenizer.decode(torch.argmax(probs))
            while next_word[0].isalpha():
                word = f"{word}{next_word}"
                input_ids = self.tokenizer(f"{prompt}{word}", return_tensors="pt")["input_ids"].to(self.device)
                output = self.model(input_ids=input_ids)
                logits = output.logits[0, -1, :]
                probs = torch.softmax(logits, dim=-1)
                next_word = self.tokenizer.decode(torch.argmax(probs))
                if len(word) > 20:
                    if len(og_word) <= 2:
                        og_word += "eds"
                    return og_word
        return word

    def _get_permutations(self):
        return_list = []
        for i in range(len(self.words_to_guess)):
            extendy = list(itertools.combinations(self.words_to_guess, i+1))
            return_list.extend(extendy)
        return return_list

    def card_guessed(self, word):
        if word in self.words_to_guess:
            self.words_to_guess.remove(word)
        elif word in self.words_to_not_guess:
            self.words_to_not_guess.remove(word)
        else:
            print(f"THE OFFENDING WORD:{word}")
            print(f"WORDS TO GUESS:{self.words_to_guess}")
            print(f"WORDS TO NOT GUESS:{self.words_to_not_guess}")
            raise Exception("That word is not present!")

    def _make_dataset(self, permutation, clue):
        prompt = self._make_prompt(permutation)
        dictionary = {"prompt": prompt, "answer": clue}
        with open(self._dataset_file, 'ab') as f:
            pickle.dump(dictionary, f)

