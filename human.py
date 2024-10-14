class Human:
    def __init__(self, blue_words, red_words, other_words):
        self.blue_words = blue_words
        self.red_words = red_words
        self.other_words = other_words

    def guess_is_good(self, guess):
        guess = guess.lower()
        if guess in self.blue_words:
            return True
        elif guess in self.red_words:
            return True
        elif guess in self.other_words:
            return True
        return False

    def card_guessed(self, word):
        if word in self.blue_words:
            self.blue_words.remove(word)
        elif word in self.red_words:
            self.red_words.remove(word)
        elif word in self.other_words:
            self.other_words.remove(word)
        else:
            raise Exception("That word is not present!")

    def get_clue(self):
        print(f"BLUE WORDS: {self.blue_words}")
        print(f"RED WORDS: {self.red_words}")
        print(f"OTHER WORDS: {self.other_words[:-1]}")
        print(f"BLACK WORD: {self.other_words[-1]}")
        how_many = int(input("How many words do you want them to guess?\n"))
        while how_many <= 0 or how_many > 9:
            print("That is not a valid number")
            how_many = int(input("How many words do you want them to guess?\n"))
        empty = []
        for i in range(how_many):
            empty.append(i)
        return 0, 0, 0, empty, input("What CLUE do you want to give?\n"), 0

    def get_guess(self, clue, amount):
        guesses = []
        for i in range(amount):
            guess = input(f"Clue: {clue}\nAmount: {amount}\n(type in one word and hit enter\n")
            while not self.guess_is_good(guess):
                print("That is not a valid guess.")
                guess = input(f"Clue: {clue}\nAmount: {amount}\n(type in one word and hit enter\n")

            guesses.append(guess)
        return guesses
