class PlayGame:
    def __init__(self, red_clue_giver, blue_clue_giver, red_guesser, blue_guesser, red_words, blue_words, other_words, black_word):
        self.red_clue_giver = red_clue_giver
        self.blue_clue_giver = blue_clue_giver
        self.red_guesser = red_guesser
        self.blue_guesser = blue_guesser
        self.red_words = red_words
        self.blue_words = blue_words
        self.other_words = other_words
        self.black_word = black_word
        self.red_words_guessed = 0
        self.blue_words_guessed = 0
        self.reds_turn = bool(len(self.red_words) > len(self.blue_words))

    def get_board(self):
        board = ""
        board += "RED WORDS\n"
        for word in self.red_words:
            board += f"{word}\n"

        board += "\nBLUE WORDS\n"
        for word in self.blue_words:
            board += f"{word}\n"

        board += "\nTAN WORDS\n"
        for word in self.other_words:
            board += f"{word}\n"

        board += "\nBLACK WORD\n"
        board += f"{self.black_word}\n"
        return board

    def do_turn(self, quiet=False):
        if self.reds_turn:
            if not quiet:
                print("RED TURN")
            self.reds_turn = not self.reds_turn
            _, _, _, words_that_it_wants_to_be_guessed, clue, _ = self.red_clue_giver.get_clue()
            if not quiet:
                print(f"WORDS THAT RED WANTS TO BE GUESSED: {words_that_it_wants_to_be_guessed}")
                print(f"THE HINT RED GAVE: {clue}")

            sorted_guesses = self.red_guesser.get_guess(clue, len(words_that_it_wants_to_be_guessed))

            for guess in sorted_guesses:
                if len(self.red_words) == self.red_words_guessed:
                    if not quiet:
                        print(f"Len of red_words: {len(self.red_words)}")
                        print(f"amount of red_words guessed: {self.red_words_guessed}")
                        print("ALL RED WORDS GUESSED!")
                        print("RED WINS!!!")
                    return False, "red", "all"

                if len(self.blue_words) == self.blue_words_guessed:
                    if not quiet:
                        print(f"Len of blue_words: {len(self.blue_words)}")
                        print(f"amount of blue_words guessed: {self.blue_words_guessed}")
                        print("ALL BLUE WORDS GUESSED!")
                        print("BLUE WINS!!!")
                    return False, "blue", "all"

                if guess == self.black_word:
                    if not quiet:
                        print(f"RED GUESSED {guess} WHICH IS THE WORD THAT ENDS THE GAME")
                        print("BLUE WINS!!!")
                    return False, "blue", "black"
                self.red_clue_giver.card_guessed(guess)
                self.blue_clue_giver.card_guessed(guess)
                self.red_guesser.card_guessed(guess)
                self.blue_guesser.card_guessed(guess)
                if guess in self.blue_words:
                    if not quiet:
                        print(f"RED GUESSED {guess} WHICH IS A BLUE WORD.")
                        print("TURN OVER")
                    self.blue_words_guessed += 1
                    return True, None, None
                if guess in self.other_words:
                    if not quiet:
                        print(f"RED GUESSED {guess} WHICH IS A TAN WORD.")
                        print("TURN OVER")
                    return True, None, None
                self.red_words_guessed += 1
                if not quiet:
                    print(f"RED GUESSED {guess} WHICH IS A RED WORD.")

        else:
            if not quiet:
                print("BLUE TURN")
            self.reds_turn = not self.reds_turn
            _, _, _, words_that_it_wants_to_be_guessed, clue, _ = self.blue_clue_giver.get_clue()
            if not quiet:
                print(f"WORDS THAT BLUE WANTS TO BE GUESSED: {words_that_it_wants_to_be_guessed}")
                print(f"THE HINT BLUE GAVE: {clue}")
                print(f"THE AMOUNT OF WORDS THAT SHOULD BE GUESSED: {len(words_that_it_wants_to_be_guessed)}")

            sorted_guesses = self.blue_guesser.get_guess(clue, len(words_that_it_wants_to_be_guessed))

            for guess in sorted_guesses:
                if len(self.red_words) == self.red_words_guessed:
                    if not quiet:
                        print("ALL RED WORDS GUESSED!")
                        print("RED WINS!!!")
                    return False, "red", "all"

                if len(self.blue_words) == self.blue_words_guessed:
                    if not quiet:
                        print("ALL BLUE WORDS GUESSED!")
                        print("BLUE WINS!!!")
                    return False, "blue", "all"

                if guess == self.black_word:
                    if not quiet:
                        print(f"BLUE GUESSED {guess} WHICH IS THE WORD THAT ENDS THE GAME")
                        print("RED WINS!!!")
                    return False, "red", "black"
                self.red_clue_giver.card_guessed(guess)
                self.blue_clue_giver.card_guessed(guess)
                self.red_guesser.card_guessed(guess)
                self.blue_guesser.card_guessed(guess)
                if guess in self.red_words:
                    if not quiet:
                        print(f"BLUE GUESSED {guess} WHICH IS A RED WORD.")
                        print("TURN OVER")
                    self.red_words_guessed += 1
                    return True, None, None
                if guess in self.other_words:
                    if not quiet:
                        print(f"BLUE GUESSED {guess} WHICH IS A TAN WORD.")
                        print("TURN OVER")
                    return True, None, None
                self.blue_words_guessed += 1
                if not quiet:
                    print(f"BLUE GUESSED {guess} WHICH IS A BLUE WORD.")

        if len(self.red_words) == self.red_words_guessed:
            if not quiet:
                print("ALL RED WORDS GUESSED!")
                print("RED WINS!!!")
            return False, "red", "all"

        if len(self.blue_words) == self.blue_words_guessed:
            if not quiet:
                print("ALL BLUE WORDS GUESSED!")
                print("BLUE WINS!!!")
            return False, "blue", "all"

        if not quiet:
            print("FINISHED TURN SUCCESSFULLY! CONGRATS")
            print("TURN OVER")
        return True, None, None
