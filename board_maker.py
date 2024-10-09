import random


class BoardMaker:
    def __init__(self, file="words.txt"):
        self.file = file

    def get_words(self):
        with open(self.file, 'r') as f:
            lines = [line.rstrip().lower() for line in f]

        indices = random.sample(range(len(lines)), 25)
        words = []
        for index in indices:
            words.append(lines[index])

        red_words = 8 + random.randint(0, 1)
        blue_words = 17
        return words[:red_words], words[red_words:blue_words], words[blue_words:25]
