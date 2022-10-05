import numpy as np
from collections import defaultdict


class TicTacToeQTable:

    def __init__(self, initial_q=1, ):
        self.store = defaultdict(lambda: [initial_q] * 9)
        self.prev_state = None
        self.prev_board = None
        self.prev_mark = None

    def get_row(self, board, mark):        
        board = np.array(board.copy())
        found = False
        for i in range(4):
            state = self.get_state_hash(board, mark)
            if not found and state in self.store:
                found = True
                q = np.array(self.store[state])
            elif not found and state not in self.store:
                board = self.rotate90(board)
            else:
                q = self.rotate90(q)
        return q

    def rotate90(self, board):
        return np.array(board)[[6,3,0,7,4,1,8,5,2]]

    def get_state_hash(self, board, mark, state=None):
        return ''.join([*[str(x) for x in board], str(mark)])

    def __iter__(self):
        return iter(self.store)
    
    def __len__(self):
        return len(self.store)

    # TODO finish q table for rotational symmetry
