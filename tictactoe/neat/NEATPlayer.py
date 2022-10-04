import time
import neat

from numpy import argmax

from tictactoe.Player import AIPlayer

class NEATPlayer(AIPlayer):

    def __init__(this, network, delay=0, name=None):
        super().__init__(name)
        this.network = network
        this.delay = delay

    def _make_move(this, board, retry):
        if retry:
            this.num_bad_moves += 1
            return board.index(0)
        input = this.format_input(board)
        return argmax(this.network.activate(input))

    def format_input(this, board):
        return (*[float(x)/2 for x in board], float(this.mark)/2)