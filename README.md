# CodeNames
Plays CodeNames. Automatically generated contextually based clues. Unique algorithm. 

This uses Encoder style Transformer networks to play the party game Code Names. The basic algorithm is quite simple.

**X**n is all words in play that are negative words that should not be represented in the clue given.

**X**p is all words in play that are positive words that could be represented in the clue given. 

For all permutations of **X**p (where (Xi, Xj) == (Xj, Xi)) obtain their outputs from f(permutations(**X**p)) where f is an encoder model.

Find the individual output such that MAX(f(permutation(**X**p)) - f(**X**n))

And there you go, that's your clue. 

This simple approach leverages LLM's ability to use context, while also enforcing rule following and avoiding instability when using LLMs. Some of the benefits to this approach is that every guess and every turn of the game shuffles the state of the game, updating the logits and thus the clues the model gives. CodeNames with contextual clues. 
