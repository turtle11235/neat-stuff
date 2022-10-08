from collections.abc import MutableMapping
import numpy as np
from collections import defaultdict


class TicTacToeQTable:

    def __init__(self, initial_q, table={}):
        self.store = defaultdict(lambda: [initial_q] * 9, **table)
        self.prev_state = None
        self.prev_board = None
        self.prev_mark = None

    def __iter__(self):
        return iter(self.store)
    
    def __len__(self):
        return len(self.store)

    def __contains__(self, key):
        return key in self.store

    def __repr__(self) -> str:
        return self.store.__repr__()

    def get_row(self, board, mark):
        rotated = board.copy()
        for i in range(4):
            state = self.get_state_hash(rotated, mark)
            if state in self.store:
                return self.rotate90(self.store[state], -i)
            else:
                rotated = self.rotate90(rotated)

        state = self.get_state_hash(board, mark)
        return self.store[state]

    def get_q(self, board, mark, move):
        return self.get_row(board, mark)[move]

    def set_q(self, board, mark, move, q):
        rotated_board = board.copy()
        rotated_move = move
        for i in range(4):
            state = self.get_state_hash(rotated_board, mark)
            if state in self.store:
                self.store[state][rotated_move] = q
                break
            else:
                rotated_board = self.rotate90(rotated_board)
                rotated_move = self.rotate90(rotated_move)
        else:
            state = self.get_state_hash(board, mark)
            self.store[state][move] = q
        
    def _unhash_state(self, state):
        board = np.array([int(x) for x in state[::-1]])
        mark = int(state[-1])
        return board, mark

    def _rotate90(self, a):
        try:
            a = int(a)
            rotated = np.arange(9)[[6,3,0,7,4,1,8,5,2]]
            return np.where(rotated == a)[0][0]
        except TypeError:
            return np.array(a)[[6,3,0,7,4,1,8,5,2]]

    def rotate90(self, a, n=1):
        for i in range(n % 4):
            a = self._rotate90(a)
        return a

    def rotate_index90(self, index):
        rotated = self.rotate90(list(range(9)))
        return rotated.index(index)

    def get_state_hash(self, board, mark, state=None):
        return ''.join([*[str(x) for x in board], str(mark)])