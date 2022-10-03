import os
import random

import neat
import visualize

from AIPlayer import AIPlayer
from Game import Game


def derange(items):
    original = items.copy()
    derangement = []
    for i in range(len(items)):
        item = random.choice(original)
        while items[i] == item:
            item = random.choice(original)
        original.remove(item)
        derangement.append(item)
    return derangement
        

def eval_genomes(genomes, config):
    for (genome1_id, genome1), (genome2_id, genome2) in zip(genomes, derange(genomes)):
        genome1.fitness = genome1.fitness if genome1.fitness else 0
        genome2.fitness = genome2.fitness if genome2.fitness else 0

        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        player1 = AIPlayer(net1, name=f'Bot {genome1_id}')
        player2 = AIPlayer(net2, name=f'Bot {genome2_id}')
        
        Game().play()
        
        genome1.fitness += player1.fitness
        genome2.fitness += player2.fitness


def run(config_file):
    # Load configuration.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 10)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    

    # node_names = {-1: 'A', -2: 'B', 0: 'A XOR B'}
    # visualize.draw_net(config, winner, True, node_names=node_names)
    # visualize.draw_net(config, winner, True, node_names=node_names, prune_unused=True)
    # visualize.plot_stats(stats, ylog=False, view=True)
    # visualize.plot_species(stats, view=True)

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)