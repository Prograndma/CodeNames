import time
import itertools
import torch


class ComplicatedClueGuesser:
    def __init__(self, model, tokenizer, game_words, device,
                 primer="Here is a list of unique words that are related to each other: [ "):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.words_to_guess = game_words
        self.primer = primer

    def get_guess(self, clue, amount):
        permutations = self._get_permutations(amount)
        max_prob_for_clue = 0.0
        clue_index = self._get_clue_index(clue)
        best_permutation = []
        now = time.time()
        # print(f"Testing clue on {len(permutations)} different word combinations")

        for permutation in permutations:
            prompt = self._make_prompt(permutation)
            probs = self._get_probabilities(prompt)
            current_prob = probs[clue_index].item()
            if current_prob > max_prob_for_clue:
                max_prob_for_clue = current_prob
                best_permutation = permutation

        # print(f"Testing took {time.time() - now} seconds")

        sorted_best_permutation = self._get_word_probs(best_permutation, clue)

        return sorted_best_permutation

    def _get_clue_index(self, clue):
        input_ids = self.tokenizer(clue, return_tensors="pt")["input_ids"].to(self.device)
        return input_ids[0, 0]

    def _get_permutations(self, amount):
        return list(itertools.combinations(self.words_to_guess, amount))

    def _make_prompt(self, words):
        prompt = self.primer
        for word in words:
            prompt = f"{prompt}{word}, "
        return prompt

    def _get_probabilities(self, prompt):
        input_ids = self.tokenizer(prompt, return_tensors="pt")["input_ids"].to(self.device)
        with torch.no_grad():
            output = self.model(input_ids=input_ids)
            logits = output.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1)
        return probs

    def _get_word_probs(self, words, clue):
        indices = []
        probs = []

        probs_distribution = self._get_probabilities(self._make_prompt([clue]))

        for word in words:
            indices.append(self.tokenizer(word, return_tensors="pt")["input_ids"].to(self.device)[0, 0])

        for index in indices:
            probs.append(probs_distribution[index])

        return self.sort_words_based_on_probs(words, probs)

    @staticmethod
    def sort_words_based_on_probs(words, probs):
        zipped_pairs = zip(probs, words)
        z = [x for _, x in sorted(zipped_pairs)]
        return z

    def card_guessed(self, word):
        if word in self.words_to_guess:
            self.words_to_guess.remove(word)
        else:
            raise Exception("That word is not present!")
