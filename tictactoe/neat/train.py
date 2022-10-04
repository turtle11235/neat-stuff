"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
from distutils.command import check
import os
import neat
from numpy import true_divide
import visualize
import random
import argparse

from NEATPlayer import NEATPlayer
from ..tictactoe import TicTacToe
from ..Player import HumanPlayer


def derange(items):
    while True:
        original = items.copy()
        derangement = []
        for i in range(len(items)):
            item = random.choice(original)
            if items[i] == item and len(derangement) == len(original) - 1:
                break
            while items[i] == item:
                item = random.choice(original)
            original.remove(item)
            derangement.append(item)
            return derangement

def calculate_fitness(player):
    if player.num_bad_moves > 0:
        return -player.num_bad_moves / player.num_games
    else:
        return (player.num_wins + .5 * player.num_ties) / player.num_games

def eval_genomes(genomes, config):
    players = [NEATPlayer(neat.nn.FeedForwardNetwork.create(g, config), name=f"Bot {id}") for id, g in genomes]

    for player1, (genome1_id, genome1) in zip(players, genomes):
        for player2, (genome2_id, genome2) in zip(players, genomes):
            if genome1_id == genome2_id:
                continue
            
            TicTacToe().play(player1, player2, display=False)
            
            genome1.fitness = calculate_fitness(player1)
            genome2.fitness = calculate_fitness(player2)

def run(config_file, checkpoint_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(10, filename_prefix=f'{checkpoint_file}/checkpoint-'))

    # Run for up to 1000 generations.
    winner = p.run(eval_genomes, 5000)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    winner_player = NEATPlayer(winner_net, delay=1, name=f"Bot {winner.key}")
    TicTacToe().play(HumanPlayer(), winner_player, n_games=-1, display=True)

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    parser = argparse.ArgumentParser(description='Use NEAT to evolve a neural network that plays tic tac toe')
    parser.add_argument('config', metavar='C', type=str, help='name of the config file')
    parser.add_argument('--checkpoint', '-c', dest="checkpoint", metavar='CP', type=str,
                    help='name of the config file', default=None)
    args = parser.parse_args()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, f'configs/{args.config}')
    checkpoint_path = os.path.join(local_dir, f'checkpoints/{args.checkpoint}') if args.checkpoint else os.path.join(local_dir, f'checkpoints/{args.config}')
    os.makedirs(checkpoint_path, exist_ok=True)
    run(config_path, checkpoint_path)