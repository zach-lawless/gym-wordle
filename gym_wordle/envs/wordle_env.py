import gym
from gym import spaces
import numpy as np
import random
from typing import Optional

# global game variables
GAME_LENGTH = 6
WORD_LENGTH = 5

# load encoded words
file = open("../../data/words_encoded.txt", "r")
lines = file.readlines()
WORDS = [tuple(int(num) for num in line.strip().split()) for line in lines]


class WordleEnv(gym.Env):
    """
    Simple Wordle Environment

    Wordle is a guessing game where the player has 6 guesses to guess the
    5 letter hidden word. After each guess, the player gets feedback on the
    board regarding the word guessed. For each character in the guessed word:
        * if the character is not in the hidden word, the character is
          grayed out (encoded as 0 in the environment)
        * if the character is in the hidden word but not in correct
          location, the character is yellowed out (encoded as 1 in the
          environment)
        * if the character is in the hidden word and in the correct
          location, the character is greened out (encoded as 2 in the 
          environment)
    
    The player continues to guess until they have either guessed the correct
    hidden word, or they have run out of guesses.

    The environment is structured in the following way:
        * Action Space: the action space is a length 5 Box where valid values
          are [0, 25], corresponding to characters [a, z].
        * Observation Space: the observation space is tuple consisting of
          three objects:
          - Board: The board is 6x5 Box corresponding to the history of
            guesses. At the start of the game, the board is filled entirely
            with -1 values, indicating no guess has been made. As the player
            guesses words, the rows will fill up with values in the range
            [0, 2] indicating whether the characters are missing in the
            hidden word, in the incorrect position, or in the correct position.
          - Alphabet: the alphabet is a 1x26 Box corresponding to the guess
            status for each letter in the alaphabet. As the start, all values
            are -1, as no letter has been used in a guess. As the player
            guesses words, the letters in the alphabet will change to values in
            the range [0, 2] indicating whether the characters are missing in
            the hidden word, in the incorrect position, or in the correct
            position.
          - Guesses Remaining: The guesses remaining is simply a Discrete(6)
            letting the player know how many guesses they have before the game
            ends.
    """

    def __init__(self):
        self.action_space = spaces.Box(low=0, high=25, shape=(WORD_LENGTH,), dtype=int)
        self.observation_space = spaces.Tuple(
            (spaces.Box(low=-1, high=2, shape=(GAME_LENGTH, WORD_LENGTH), dtype=int),
             spaces.Box(low=-1, high=2, shape=(26,), dtype=int),
             spaces.Discrete(GAME_LENGTH))
        )

    def step(self, action):
        assert self.action_space.contains(action)

        # update game board and alphabet tracking
        board_row_idx = GAME_LENGTH - self.guess_rem
        for idx, char in enumerate(action):
            if self.hidden_word[idx] == char:
                encoding = 2
            elif char in self.hidden_word:
                encoding = 1
            else:
                encoding = 0

            self.board[board_row_idx, idx] = encoding
            self.alphabet[char] = encoding

        # update guesses remaining tracker
        self.guess_rem -= 1

        # check to see if game is over
        if all(self.board[board_row_idx, :] == 2):
            reward = 1.0
            done = True
        else:
            if self.guess_rem > 0:
                reward = 0.0
                done = False
            else:
                reward = -1.0
                done = True

        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        return (self.board, self.alphabet, self.guess_rem)

    def reset(self, seed: Optional[int] = None):
        # super().reset(seed=seed)
        self.hidden_word = random.choice(WORDS)
        self.board = np.negative(np.ones(shape=(GAME_LENGTH, WORD_LENGTH), dtype=int))
        self.alphabet = np.negative(np.ones(shape=(26,), dtype=int))
        self.guess_rem = GAME_LENGTH
        return self._get_obs()
