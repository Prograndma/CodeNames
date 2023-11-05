import itertools
import numpy as np
import torch


class ClueGiver:
    def __init__(self, model, tokenizer, good_words, bad_words, device,
                 primer="Here is a list of unique words that are related to each other: [ "):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.primer = primer
        self.remove_word_indices = []
        self.words_to_guess = good_words
        self.words_to_not_guess = bad_words
        self._init_remove_words(good_words, bad_words)

    def _make_prompt(self, word_list):
        prompt = self.primer
        for word in word_list:
            prompt = f"{prompt} {word}, "
        return prompt

    def _init_remove_words(self, good_words, bad_words):
        biggest_good_prompt = self._make_prompt(good_words)
        biggest_bad_prompt = self._make_prompt(bad_words)

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
        bad_prompt = self._make_prompt(self.words_to_not_guess)
        bad_probs = self._get_probabilities(bad_prompt)

        for permutation in word_permutations:
            current_prompt = self._make_prompt(permutation)
            good_probs = self._get_probabilities(current_prompt)
            word, score, index = self._get_word_score_and_token_index(good_probs, bad_probs)
            scores.append(score)
            words.append((permutation, word, index))

        best_index = np.argmax(scores)
        words_that_you_should_guess, best_clue, index = words[best_index]
        return scores, words, scores[best_index], words_that_you_should_guess, best_clue, index

    def _get_word_score_and_token_index(self, good_probs, bad_probs):
        diff = good_probs - bad_probs
        diff_no_repeats = self._remove_repeats(diff)
        diff_no_bad_clues = self._make_sure_good_clue(diff_no_repeats)
        word = self.tokenizer.decode(torch.argmax(diff_no_bad_clues))
        score = diff_no_repeats[torch.argmax(diff_no_bad_clues)].item()
        index = torch.argmax(diff_no_bad_clues)
        return word, score, index

    def _make_sure_good_clue(self, probs):
        clue = self.tokenizer.decode(torch.argmax(probs))
        while len(clue) <= 2:
            probs[torch.argmax(probs)] = -1
            clue = self.tokenizer.decode(torch.argmax(probs))
        return probs
        #####################################

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
            raise Exception("That word is not present!")
