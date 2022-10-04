import numpy as np
from collections import defaultdict

from tictactoe.tictactoe import TicTacToe
from tictactoe.qlearning.QPLayer import QPlayer

# constants
initial_q = 1
max_games = 1
rewards = {
    'win': 100,
    'lose': -100,
    'tie': 10,
    'bad_move': -20,
    'move': -1
}

# starting variables
vars = {
    'epsilon': .5,
    'learning_rate': .5,
    'discount_factor': 1,
    'lookahead': 1
}

q_table = defaultdict([initial_q] * 9)

for i in range(max_games):

    player1 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i*2}")
    player2 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i*2 + 1}")

    TicTacToe().play(player1, player2, display=True)

