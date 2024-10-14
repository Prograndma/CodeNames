import time
import torch


class SimpleClueGuesser:
    def __init__(self, model, tokenizer, game_words, device,
                 primer="Here is a list of unique words that are related to each other: [ "):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.words_to_guess = game_words
        self.primer = primer

    def get_guess(self, clue, amount):
        probs_given_clue = self._get_probabilities(self._make_prompt(clue))
        game_indices = self._get_game_ids()
        now = time.time()
        # print("Choosing words on just one permutation")
        game_probs = []
        for index in game_indices:
            game_probs.append(probs_given_clue[index])

        sorted_words = self.sort_words_based_on_probs(self.words_to_guess, game_probs)

        print(f"Testing took {time.time() - now} seconds")
        return sorted_words[:amount]

    def _make_prompt(self, clue):
        return f"{self.primer}{clue}, "

    def _get_game_ids(self):
        indices = []
        for word in self.words_to_guess:
            indices.append(self.tokenizer(word, return_tensors="pt")["input_ids"].to(self.device)[0, 0])
        return indices

    def _get_probabilities(self, prompt):
        input_ids = self.tokenizer(prompt, return_tensors="pt")["input_ids"].to(self.device)
        with torch.no_grad():
            output = self.model(input_ids=input_ids)
            logits = output.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1)
        return probs

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
