import argparse
import math
import random
import time
from xmlrpc.client import Boolean
import numpy as np
from collections import defaultdict
import json

from Player import HumanPlayer
from tictactoe import TicTacToe
from QPLayer import QPlayer
from TicTacToeQTable import TicTacToeQTable

# constants
initial_q = 0
max_games = 5000000
checkpoint_frequency = 50000
rewards = {
    'win': 100,
    'lose': -100,
    'tie': 10,
    'bad_move': -20,
    'move': -1
}
# epsilon_decay = 1 - 1e-6
# discount_decay = 1 - 1e-6
# learning_decay = 1 - 1e-6

def create_step_decay_variable(start, end, steps):
    step_size = (end - start) / steps
    return lambda step: start + (step_size * step)

def checkpoint(q_table, vars, total_time, checkpoint_time, game):
    print(f"*** GAME {game} ***\n")
    print(f"state size={len(q_table)}, epsilon={vars['epsilon']:.2f}, discount={vars['discount_factor']:.2f}, learning rate={vars['learning_rate']:.2f}")
    print(f"cp time={(checkpoint_time):.2f} sec, total time={total_time:.2f} sec\n")
    for k, v in random.sample(list(q_table.store.items()), k=min(10, len(q_table))):
        print(f"  {k}:\t{v}")
    print()
    with open('q_checkpoint_v2.json', 'w') as fp:
        json.dump({
            'vars': vars,
            'rewards': rewards, 
            'current_game': game, 
            'max_games': max_games,
            'checkpoint_frequency': checkpoint_frequency,
            'total_time': total_time,
            'initial_q': initial_q,
            'q_table': q_table.store
        }, fp)
    checkpoint_time = time.time()

def initialize_training_from_checkpoint():
    with open('q_checkpoint.json', 'r') as f:
        checkpoint = json.load(f)
        for k, v in checkpoint.items():
            if k in globals():
                globals()[k] = v
        return checkpoint['vars'], TicTacToeQTable(initial_q, checkpoint['q_table']), checkpoint['total_time'], checkpoint['current_game'] + 1

def initialize_training():
    # starting variables
    vars = {
        'epsilon': 1,
        'learning_rate': 0.1,
        'discount_factor': 0,
    }

    # q_table = defaultdict(lambda: [initial_q] * 9)
    q_table = TicTacToeQTable(initial_q)

    return vars, q_table, 0, 1

def train(from_checkpoint=False):

    if from_checkpoint:
        vars, q_table, total_time, starting_game = initialize_training_from_checkpoint()
        print(f"Initialized from checkpoint. Starting from game {starting_game}\n")
    else:
        vars, q_table, total_time, starting_game = initialize_training()

    epsilon_decay = create_step_decay_variable(vars['epsilon'], 0, max_games-starting_game)
    discount_decay = create_step_decay_variable(vars['discount_factor'], 1, max_games-starting_game)
    learning_decay = create_step_decay_variable(vars['learning_rate'], .8, max_games-starting_game)

    checkpoint_start = time.time()
    for i in range(starting_game, max_games+1):
        player1 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i}A")
        player2 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {i}B")

        TicTacToe().play(player1, player2)

        if i == 1 or i % checkpoint_frequency == 0:
            checkpoint_time = time.time() - checkpoint_start
            total_time += checkpoint_time
            checkpoint(q_table, vars, total_time, checkpoint_time, i)
            checkpoint_start = time.time()

        vars['epsilon'] = epsilon_decay(i)
        vars['discount_factor'] = discount_decay(i)
        vars['learning_rate'] = learning_decay(i)

    print("Final result:")
    for k, v in random.sample(list(q_table.store.items()), k=min(50, len(q_table))):
        print(f"  {k}:\t{v}")
    print()

    vars['epsilon'] = 0
    player1 = HumanPlayer()
    player2 = QPlayer(q_table, rewards=rewards, variables=vars, name=f"Bot {max_games}", delay=1)
    TicTacToe().play(player1, player2, n_games=-1, display=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', default=False, dest='from_checkpoint', action='store_true')
    args = parser.parse_args()
    train(args.from_checkpoint)