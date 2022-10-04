from cmath import inf
import random
from tictactoe import TicTacToe
from Player import AIPlayer
import numpy as np
from numpy import argmax, where

class QPlayer(AIPlayer):

    def __init__(this, q_table, rewards, variables, name=None, delay=0):
        super().__init__(delay, name)

        this.q_table = q_table

        this.rewards = rewards
        this.variables = variables

        this.prev_state = None
        this.prev_move = None

        this.prev_states = []
        this.prev_moves = []

    def is_new_game(this, board):
        n_moves = len(np.where(np.array(board) != 0)[0])
        if n_moves == 0 or n_moves == 1:
            return True
        else:
            return False

    def _make_move(this, board, retry):
        # if retry:
        #    this.update_q(board, this.prev_move, this.rewards['bad_move'])
            
        move = this.get_move(board, retry)
        this.prev_state = this.board_to_state(board)
        this.prev_move = move
        if this.is_new_game(board):
            this.prev_states = []
            this.prev_moves = []
        this.prev_states.append(this.prev_state)
        this.prev_moves.append(this.prev_move)
        return move

    def get_move(this, board, retry=False):
        if not retry and random.random() > this.variables['epsilon']:
            return this.get_greedy_move(board)
        else:
            return this.get_random_move(board)

    def get_random_move(this, board):
        valid_moves = np.where(np.array(board) == 0)[0]
        return random.choice(valid_moves)

    def get_greedy_move(this, board):
        state = this.board_to_state(board)
        q_vals = this.q_table[state]
        max_q = -np.inf
        greedy_move = None
        for i in range(len(board)):
            if board[i] == 0 and q_vals[i] > max_q:
                max_q = q_vals[i]
                greedy_move = i
        return greedy_move

    def board_to_state(this, board, mark=None):
        if mark is None:
            mark = this.mark
        return ''.join((*[str(x) for x in board], str(this.mark)))

    def state_to_board(this, state):
        *board, _ = [int(x) for x in state]
        return board
    
    def update_q_table(this, reward):
        alpha = this.variables['learning_rate']
        gamma = this.variables['discount_factor']

        future_q = None
        for state, move, i in zip(this.prev_states[::-1], this.prev_moves[::-1], range(len(this.prev_states))):
            curr_q = this.q_table[state][move]
            if i > 0:
                updated_q = curr_q + alpha * (gamma * future_q - curr_q)
            else:
                updated_q = curr_q + alpha * (reward - curr_q)
            future_q = updated_q
            this.q_table[state][move] = updated_q
            
    def get_future_value(this, state):
        current_board = this.state_to_board(state)
        
        opp_mark = this.get_opponent_mark()
        opp_state = this.board_to_state(current_board, opp_mark)
        opp_best_move = argmax(this.q_table[opp_state])

        future_board = current_board.copy()
        future_board[opp_best_move] = opp_mark
        future_state = this.board_to_state(future_board)

        return max(this.q_table[future_state])

    def get_opponent_mark(this):
        return 1 if this.mark == 2 else 2

    def win(this):
        super().win()
        # board = this.state_to_board(this.prev_state)
        # this.update_q(board, this.prev_move, this.rewards['win'])
        this.update_q_table(this.rewards['win'])

    def lose(this):
        super().win()
        this.update_q_table(this.rewards['lose'])

    def tie(this):
        super().win()
        this.update_q_table(this.rewards['tie'])
        
