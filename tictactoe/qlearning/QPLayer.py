from cmath import inf
from tictactoe.tictactoe import TicTacToe
from ..Player import Player

class QPlayer(Player):

    def __init__(this, q_table, rewards, variables, name=None):
        super().__init__(name)

        this.q_table = q_table

        this.rewards = rewards
        this.variables = variables

        this.prev_state = None
        this.prev_move = None

    def _make_move(this, board, retry):
        if retry:
            this.update_q(this.rewards['bad_move'])
            
        move = this.get_move(board)
        this.prev_state = this.board_to_state(board)
        this.prev_move = move

    def get_move(this):
        pass

    def get_random_move(this):
        pass

    def get_greedy_move(this):
        pass

    def board_to_state(this, board):
        return (*board, this.mark).join('')

    def state_to_board(this, state):
        *board, _ = [int(x) for x in state]
        return board
    

    def update_q(this, reward):
        state = this.board_to_state(board)
        curr_q = this.q_table[state][this.prev_move]
        alpha = this.variables['learning_rate']
        gamma = this.variables['discount_rate']
        max_q = this.get_future_value(state)

        updated_q = curr_q + alpha * (reward + gamma * max_q - curr_q)
        this.q_table[state][]

    def get_reward(this, board, move):
        from tictactoe.tictactoe import TicTacToe
        game = TicTacToe()

        if not game.is_available(move, board):
            return this.rewards['bad_move']
        
        board = board.copy()
        board[move] = this.mark
        res = game.check_win(board)
        if res == 1:
            return this.rewards['win']
        elif res == 0:
            return this.rewards['move']

    def get_future_value(this, state):
        from tictactoe.tictactoe import TicTacToe
        game = TicTacToe()

        current_board = this.state_to_board(state)
        
        opp_max_q = -inf
        opp_best_move = None
        for i in range(len(current_board)):
            opp_q = this.get_reward(current_board, i)
            if opp_q > opp_max_q:
                opp_max_q = opp_q
                opp_best_move = i

        future_board = current_board.copy()
        future_board[opp_best_move] = this.get_opponent_mark()
        if game.check_win(future_board) == 1:
            return this.rewards['lose']
        elif game.check_win(future_board) == 0:
            return this.rewards['tie']

        max_q = -inf
        for i in range(len(future_board)):
            future_q = this.get_reward(future_board, i)
            if future_q > max_q:
                max_q = future_q

        return max_q                  

    def get_opponent_mark(this):
        return 1 if this.mark == 2 else 2
