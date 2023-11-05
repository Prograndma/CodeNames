from clue_giver import ClueGiver
from complicated_clue_guesser import ComplicatedClueGuesser
from simple_clue_guesser import SimpleClueGuesser
from human import Human
from play_game import PlayGame
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    gpt = 'gpt2'

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"DEVICE IS : {device}")

    if device != 'cuda':
        return

    gpt_tokenizer = AutoTokenizer.from_pretrained(gpt)
    gpt_model = AutoModelForCausalLM.from_pretrained(gpt).to(device)
    print("loaded models and tokenizers")
    red_words = ["ham", "hole", "tie", "pistol", "moon", "plot", "well", "mug", "swing"]
    blue_words = ["knife", "car", "suit", "cliff", "game", "needle", "boom", "key"]
    bad_words = ["comic", "circle", "cat", "scorpion", "mount", "washer", "press", "stream"]

    ClueGiverRed = ClueGiver(gpt_model, gpt_tokenizer, red_words.copy(), blue_words.copy() + bad_words.copy(), device)
    ClueGiverBlue = ClueGiver(gpt_model, gpt_tokenizer, blue_words.copy(), red_words.copy() + bad_words.copy(), device)

    ComplicatedClueGuesserRed = ComplicatedClueGuesser(gpt_model, gpt_tokenizer,
                                                       red_words.copy() + blue_words.copy() + bad_words.copy(), device)

    ComplicatedClueGuesserBlue = ComplicatedClueGuesser(gpt_model, gpt_tokenizer,
                                                        red_words.copy() + blue_words.copy() + bad_words.copy(), device)
    SimpleClueGuesserBlue = SimpleClueGuesser(gpt_model, gpt_tokenizer,
                                              red_words.copy() + blue_words.copy() + bad_words.copy(), device)

    HumanClueGiverBlue = Human(blue_words, red_words, bad_words)

    game_player = PlayGame(HumanClueGiverBlue, ClueGiverBlue, ComplicatedClueGuesserRed, SimpleClueGuesserBlue,
                           red_words.copy(), blue_words.copy(), bad_words.copy(), "stream")

    print("Starting first round of the game")
    while game_player.do_turn():
        print("######################################################################")
        print("######################################################################")
        print("######################################################################")
        print("\n\n")
        print("######################################################################")
        print("######################################################################")
        print("######################################################################")


if __name__ == "__main__":
    main()
