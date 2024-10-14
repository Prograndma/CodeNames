from clue_giver import ClueGiver
from complicated_clue_guesser import ComplicatedClueGuesser
from simple_clue_guesser import SimpleClueGuesser
from human import Human
from play_game import PlayGame
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from board_maker import BoardMaker
from game_tester import GameTester


def get_game(device, tokenizer, red_giver_trained=False, red_guesser_trained=False):

    red_words, blue_words, bad_words = BoardMaker().get_words()
    model = AutoModelForCausalLM.from_pretrained('gpt2').to(device)
    my_model = AutoModelForCausalLM.from_pretrained("trained_codenames/checkpoint-500").to(device)

    if red_giver_trained:
        clue_giver_red = ClueGiver(my_model, tokenizer, red_words.copy(), blue_words.copy() + bad_words.copy(), device)
    else:
        clue_giver_red = ClueGiver(model, tokenizer, red_words.copy(), blue_words.copy() + bad_words.copy(), device)

    if red_guesser_trained:
        complicated_clue_guesser_red = ComplicatedClueGuesser(my_model,
                                                              tokenizer,
                                                              red_words.copy() + blue_words.copy() + bad_words.copy(),
                                                              device)
    else:
        complicated_clue_guesser_red = ComplicatedClueGuesser(model,
                                                              tokenizer,
                                                              red_words.copy() + blue_words.copy() + bad_words.copy(),
                                                              device)

    clue_giver_blue = ClueGiver(model, tokenizer, blue_words.copy(), red_words.copy() + bad_words.copy(), device)
    complicated_clue_guesser_blue = ComplicatedClueGuesser(model,
                                                           tokenizer,
                                                           red_words.copy() + blue_words.copy() + bad_words.copy(),
                                                           device)

    game_player = PlayGame(clue_giver_red, clue_giver_blue, complicated_clue_guesser_red, complicated_clue_guesser_blue,
                           red_words.copy(), blue_words.copy(), bad_words.copy(), bad_words[-1])
    return game_player


def test_game(device, clue_giver_model, clue_giver_tokenizer, clue_guesser_model, clue_guesser_tokenizer, how_many):
    red_wins = 0
    red_losses_black = 0
    red_losses_guessed_all_blue = 0
    turns_taken = []
    for _ in range(how_many // 2):
        print("#", end="")
    print("")
    for i in range(how_many):
        if i % 2 == 0:
            print("#", end="")
        red_words, blue_words, bad_words = BoardMaker().get_words()
        clue_giver_red = ClueGiver(clue_giver_model, clue_giver_tokenizer, red_words.copy(),
                                   blue_words.copy() + bad_words.copy(), device)
        complicated_clue_guesser_red = ComplicatedClueGuesser(clue_guesser_model, clue_guesser_tokenizer,
                                                              red_words.copy() + blue_words.copy() + bad_words.copy(),
                                                              device)
        game_tester = GameTester(clue_giver_red, complicated_clue_guesser_red, red_words.copy(), blue_words.copy(),
                                 bad_words.copy(), bad_words[-1])
        print(game_tester.get_board())
        done = False
        amount_turns = 0
        while not done:
            _, who_won, reason_for_winning = game_tester.do_turn(quiet=True)
            amount_turns += 1
            if who_won is not None:
                done = True
                turns_taken.append(amount_turns)
                if who_won == "red":
                    red_wins += 1
                elif reason_for_winning == "black":
                    red_losses_black += 1
                else:
                    red_losses_guessed_all_blue += 1
    print("")
    avg = 0
    min_turns = 1000000
    max_turns = 0
    for turn in turns_taken:
        avg += turn
        if turn > max_turns:
            max_turns = turn
        if turn < min_turns:
            min_turns = turn
    print(f"Red Wins Out of How Many Games:   {red_wins}/{how_many}")
    print(f"Red Losses For Guessing Black:    {red_losses_black}/{red_losses_black + red_losses_guessed_all_blue}")
    print(f"Red Losses For Guessing All Blue: {red_losses_guessed_all_blue}/"
          f"{red_losses_black + red_losses_guessed_all_blue}")
    print(f"Average turns taken:              {avg / how_many}")
    print(f"The Longest Game:                 {max_turns}")
    print(f"The Shortest Game:                {min_turns}")


def play_game(device, tokenizer, how_many, red_giver_trained=False, red_guesser_trained=False):
    red_wins_all_guesses = 0
    red_wins_default = 0
    blue_wins_all_guesses = 0
    blue_wins_default = 0
    winner, why = "", ""
    if red_giver_trained:
        print(f"For game where Red clue giver is trained!")
    else:
        print("For game where Red clue giver is not trained!")
    if red_guesser_trained:
        print(f"For game where Red clue guesser is trained!")
    else:
        print("For game where Red clue guesser is not trained!")
    print("###########")
    for i in range(how_many):
        game_player = get_game(device, tokenizer, red_giver_trained, red_guesser_trained)
        if i % int(how_many / 10) == 0 and i != 0:
            print("#", end="", flush=True)
        if i == 1:
            print("#", end="", flush=True)
        keep_going = True
        while keep_going:
            keep_going, winner, why = game_player.do_turn(quiet=True)
        if winner == "blue":
            if why == 'all':
                blue_wins_all_guesses += 1
            else:
                blue_wins_default += 1
        else:
            if why == "all":
                red_wins_all_guesses += 1
            else:
                red_wins_default += 1
    print("#")
    print(f"Red wins by guessing all: {red_wins_all_guesses}")
    print(f"Red wins by default: {red_wins_default}")
    print(f"Blue wins by guessing all: {blue_wins_all_guesses}")
    print(f"Blue wins by default: {blue_wins_default}")


def main():
    gpt = 'gpt2'

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"DEVICE IS : {device}")

    if device != 'cuda':
        return

    gpt_tokenizer = AutoTokenizer.from_pretrained(gpt)
    gpt_model = AutoModelForCausalLM.from_pretrained(gpt).to(device)
    print("loaded models and tokenizers")
    red_words, blue_words, bad_words = BoardMaker().get_words()
    # red_words = ["ham", "hole", "tie", "pistol", "moon", "plot", "well", "mug", "swing"]
    # blue_words = ["knife", "car", "suit", "cliff", "game", "needle", "boom", "key"]
    # bad_words = ["comic", "circle", "cat", "scorpion", "mount", "washer", "press", "stream"]

    ClueGiverRed = ClueGiver(gpt_model, gpt_tokenizer, red_words.copy(), blue_words.copy() + bad_words.copy(), device)
    ClueGiverBlue = ClueGiver(gpt_model, gpt_tokenizer, blue_words.copy(), red_words.copy() + bad_words.copy(), device)

    ComplicatedClueGuesserRed = ComplicatedClueGuesser(gpt_model, gpt_tokenizer,
                                                       red_words.copy() + blue_words.copy() + bad_words.copy(), device)

    ComplicatedClueGuesserBlue = ComplicatedClueGuesser(gpt_model, gpt_tokenizer,
                                                        red_words.copy() + blue_words.copy() + bad_words.copy(), device)
    SimpleClueGuesserBlue = SimpleClueGuesser(gpt_model, gpt_tokenizer,
                                              red_words.copy() + blue_words.copy() + bad_words.copy(), device)

    HumanClueGiverBlue = Human(blue_words, red_words, bad_words)

    human_player = Human(blue_words, red_words, bad_words)

    game_player = PlayGame(ClueGiverRed, ClueGiverBlue, ComplicatedClueGuesserRed, ComplicatedClueGuesserBlue,
                           red_words.copy(), blue_words.copy(), bad_words.copy(), bad_words[-1])
    print(game_player.get_board())

    print("Starting first round of the game")
    while game_player.do_turn()[0]:
        print("######################################################################")
        print("######################################################################")
        print("######################################################################")
        print("\n\n")
        print("######################################################################")
        print("######################################################################")
        print("######################################################################")


if __name__ == "__main__":
    # play_game('cuda', AutoTokenizer.from_pretrained('gpt2'), 50, True, True)
    # play_game('cuda', AutoTokenizer.from_pretrained('gpt2'), 50, True, False)
    # play_game('cuda', AutoTokenizer.from_pretrained('gpt2'), 50, False, True)
    # play_game('cuda', AutoTokenizer.from_pretrained('gpt2'), 50, False, False)
    # main()
    test_game('cuda', AutoModelForCausalLM.from_pretrained('gpt2').to('cuda'), AutoTokenizer.from_pretrained('gpt2'),
              AutoModelForCausalLM.from_pretrained('gpt2').to('cuda'), AutoTokenizer.from_pretrained('gpt2'), 100)
