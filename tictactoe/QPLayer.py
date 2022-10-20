from cmath import inf
import json
import random
from Player import AIPlayer
import numpy as np
from numpy import argmax, where
from TicTacToeQTable import TicTacToeQTable

class QPlayer(AIPlayer):

    def __init__(this, q_table: TicTacToeQTable, rewards=None, variables=None, learn=True, name=None, delay=0):
        super().__init__(delay, name)

        this.q_table = q_table

        this.rewards = rewards
        this.variables = variables

        this.learn = learn

        this.prev_state = None
        this.prev_move = None

        this.prev_states = []
        this.prev_boards = []
        this.prev_moves = []

    @staticmethod
    def load_from_checkpoint():
        with open('q_checkpoint_v2.json', 'r') as f:
            checkpoint = json.load(f)
            q_table = TicTacToeQTable(checkpoint['initial_q'], checkpoint['q_table'])
            return QPlayer(q_table, learn=False, delay=1, name="Q Bot")

    def is_new_game(this, board):
        n_moves = len(np.where(np.array(board) != 0)[0])
        if n_moves == 0 or n_moves == 1:
            return True
        else:
            return False

    def _make_move(this, board, retry):        
        move = this.get_move(board, retry)
        if this.learn:
            this.prev_state = this.board_to_state(board)
            this.prev_move = move
            if this.is_new_game(board):
                this.prev_states = []
                this.prev_moves = []
            this.prev_states.append(this.prev_state)
            this.prev_boards.append(board.copy())
            this.prev_moves.append(this.prev_move)
        return move

    def get_move(this, board, retry=False):
        if not this.learn or (not retry and random.random() > this.variables['epsilon']):
            return this.get_greedy_move(board)
        else:
            return this.get_random_move(board)

    def get_random_move(this, board):
        valid_moves = np.where(np.array(board) == 0)[0]
        return random.choice(valid_moves)

    def get_greedy_move(this, board):
        q_vals = this.q_table.get_row(board, this.mark)
        valid_moves = np.array(board) == 0
        combo = [q if v else -np.inf for q, v in zip(q_vals, valid_moves)]
        return np.argmax(combo)

    def board_to_state(this, board, mark=None):
        if mark is None:
            mark = this.mark
        return ''.join((*[str(x) for x in board], str(this.mark)))
    
    def update_q_table(this, reward):
        alpha = this.variables['learning_rate']
        gamma = this.variables['discount_factor']

        future_q = None
        for board, move, i in zip(this.prev_boards[::-1], this.prev_moves[::-1], range(len(this.prev_boards))):
            curr_q = this.q_table.get_q(board, this.mark, move)
            if i > 0:
                updated_q = curr_q + alpha * (gamma * future_q - curr_q)
            else:
                updated_q = curr_q + alpha * (reward - curr_q)
            this.q_table.set_q(board, this.mark, move, updated_q)
            future_q = max(this.q_table.get_row(board, this.mark))

    def get_opponent_mark(this):
        return 1 if this.mark == 2 else 2

    def win(this):
        super().win()
        if this.learn:
            this.update_q_table(this.rewards['win'])

    def lose(this):
        super().win()
        if this.learn:
            this.update_q_table(this.rewards['lose'])

    def tie(this):
        super().win()
        if this.learn:
            this.update_q_table(this.rewards['tie'])
        
