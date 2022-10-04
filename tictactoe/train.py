import math
import random
import time
import numpy as np
from collections import defaultdict
import json



# constants
initial_q = 1
max_games = 5000000
checkpoint_frequency = 50000
rewards = {
    'win': 100,
    'lose': -100,
    'tie': 10,
    'bad_move': -20,
    'move': -1
}
epsilon_decay = 1 - 1e-6



def train():
    global epsilon_decay

    # starting variables
    vars = {
        'epsilon': 1,
        'learning_rate': .3,
        'discount_factor': .3,
    }

    q_table = defaultdict(lambda: [initial_q] * 9)

    from Player import HumanPlayer
    from tictactoe import TicTacToe
    from QPLayer import QPlayer

    start_time = time.time()
    checkpoint_time = start_time

    for i in range(1, max_games+1):
        if i == 1 or i % checkpoint_frequency == 0:
            print(f"*** GAME {i} ***\nstate size: {len(q_table)}, epsilon={vars['epsilon']:.2f}, cp time={(time.time() - checkpoint_time):.2f} sec, total time={time.time() - start_time:.2f} sec")
            for k, v in random.sample(list(q_table.items()), k=min(10, len(q_table))):
                print(f"  {k}:\t{v}")
            print()
            with open('q_checkpoint.json', 'w') as fp:
                json.dump(q_table, fp)
            checkpoint_time = time.time()

        player1 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i}A")
        player2 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i}B")

        TicTacToe().play(player1, player2)

        vars['epsilon'] *= epsilon_decay

    print("Final result:")
    for k, v in random.sample(list(q_table.items()), k=50):
        print(f"  {k}:\t{v}")
    print()

    vars['epsilon'] = 0
    player1 = HumanPlayer()
    player2 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {max_games}", delay=1)
    TicTacToe().play(player1, player2, n_games=-1, display=True)


if __name__ == "__main__":
    train()