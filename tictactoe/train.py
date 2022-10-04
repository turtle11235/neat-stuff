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

# constants
initial_q = 0
max_games = 10000000
checkpoint_frequency = 50000
rewards = {
    'win': 100,
    'lose': -100,
    'tie': 10,
    'bad_move': -20,
    'move': -1
}
epsilon_decay = 1 - 1e-6
discount_decay = 1 - 1e-6
learning_decay = 1 - 1e-6

def checkpoint(q_table, vars, total_time, checkpoint_time, game):
    print(f"*** GAME {game} ***")
    print(f"epsilon={vars['epsilon']:.2f}, discount={vars['discount_factor']:.2f}, learning rate={vars['learning_rate']:.2f}")
    print(f"cp time={(checkpoint_time):.2f} sec, total time={total_time:.2f} sec")
    for k, v in random.sample(list(q_table.items()), k=min(10, len(q_table))):
        print(f"  {k}:\t{v}")
    print()
    with open('q_checkpoint.json', 'w') as fp:
        json.dump({
            'vars': vars,
            'rewards': rewards, 
            'epsilon_decay': epsilon_decay, 
            'discount_decay': discount_decay,
            'learning_decay': learning_decay,
            'current_game': game, 
            'max_games': max_games,
            'checkpoint_frequency': checkpoint_frequency,
            'total_time': total_time,
            'q_table': q_table
        }, fp)
    checkpoint_time = time.time()

def initialize_training_from_checkpoint():
    with open('q_checkpoint.json', 'r') as f:
        checkpoint = json.load(f)
        for k, v in checkpoint.items():
            if k in globals():
                globals()[k] = v
        return checkpoint['vars'], checkpoint['q_table'], checkpoint['total_time'], checkpoint['current_game'] + 1


def initialize_training():
    # starting variables
    vars = {
        'epsilon': 1,
        'learning_rate': 0.01,
        'discount_factor': 0,
    }

    q_table = defaultdict(lambda: [initial_q] * 9)

    return vars, q_table, 0, 1

def train(from_checkpoint=False):

    if from_checkpoint:
        vars, q_table, total_time, starting_game = initialize_training_from_checkpoint()
        print(f"Initialized from checkpoint. Starting from game {starting_game}\n")
    else:
        vars, q_table, total_time, starting_game = initialize_training()

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

        vars['epsilon'] *= epsilon_decay
        vars['discount_factor'] = 1 - ((1 - vars['discount_factor']) * discount_decay)
        vars['learning_rate'] = 1 - ((1 - vars['learning_rate']) * learning_decay)

    print("Final result:")
    for k, v in random.sample(list(q_table.items()), k=50):
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