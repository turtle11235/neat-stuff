import time
import neat

from Player import Player
from numpy import argmax

class NEATPLAYER(Player):

    def __init__(this, network, delay=0, name=None):
        super().__init__(name)
        this.network = network
        this.delay = delay

    def _make_move(this, board, retry):
        if retry:
            this.num_bad_moves += 1
            return board.index(0)
        input = this.format_input(board)
        start = time.time()
        move = argmax(this.network.activate(input))
        time.sleep(max(this.delay - (time.time() - start), 0))
        return move

    def format_input(this, board):
        return (*[float(x)/2 for x in board], float(this.mark)/2)