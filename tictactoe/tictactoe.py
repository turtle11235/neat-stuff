
import argparse
from ast import arg
import json

from Player import Player, HumanPlayer
from QPLayer import QPlayer
from TicTacToeQTable import TicTacToeQTable
# from neat.NEATPlayer import NEATPlayer

class TicTacToe:
    
    board = [0] * 9
    marks = []

    def __init__(this):
        this.player1 = None
        this.player2 = None
        this.curr_player = None
        this.next_player = None
        this.display = False

    def take_turn(this):
        this.print(f"{this.curr_player.name}, enter a move: ")
        move = this.curr_player.make_move(this.board)
        while not this.is_available(move):
            if move < 0 or move > 8:
                this.print("Move must be between 0 and 8. Enter a move: ")
            else:
                this.print(f"Position {move} is already occupied. Enter a move: ")
            move = this.curr_player.make_move(this.board, retry=True)
        this.board[move] = this.curr_player.mark
        return this.check_win()

    def is_available(this, position, board=None):
        if board:
            return position >= 0 and position <= 8 and board[position] == 0
        else:
            return position >= 0 and position <= 8 and this.board[position] == 0

    def check_win(this, board=None):
        if board is None:
            board = this.board

        
        winning_configurations = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        for winning_configuration in winning_configurations:
            mark = board[winning_configuration[0]]
            for position in winning_configuration:
                if board[position] == 0 or board[position] != mark:
                    break
            else:
                return 1
        else:
            if all(x != 0 for x in board):
                return -1
            else:
                return 0

    def switch_sides(this):
        temp = this.curr_player
        this.curr_player = this.next_player
        this.next_player = temp

    def display_board(this):
        this.print(f'''
        {this.player_to_mark(this.board[0])}|{this.player_to_mark(this.board[1])}|{this.player_to_mark(this.board[2])}
        -+-+-
        {this.player_to_mark(this.board[3])}|{this.player_to_mark(this.board[4])}|{this.player_to_mark(this.board[5])}
        -+-+-
        {this.player_to_mark(this.board[6])}|{this.player_to_mark(this.board[7])}|{this.player_to_mark(this.board[8])}

        ''')

    def player_to_mark(this, player):
        if player == 0:
            return ' '
        elif player == 1:
            return 'x'
        else:
            return 'o'

    def print(this, *args, **kwargs):
        if this.display:
            print(*args, **kwargs)

    def init_game(this, player1, player2, display):
        this.board = [0] * 9
        this.display = display

        this.player1 = player1
        this.player1.name = this.player1.name if this.player1.name else "Player 1"
        this.player1.mark = 1

        this.player2 = player2
        this.player2.name = this.player2.name if this.player2.name else "Player 2"
        this.player2.mark = 2
        
        this.curr_player = player1
        this.next_player = player2

    def play(this, player1: Player, player2: Player, n_games=1, display=False):
        n_games_played = 0

        while n_games != 0:

            this.print(f"*** GAME {n_games_played + 1} ***")

            if n_games_played % 2 == 0:
                this.init_game(player1, player2, display)
            else:
                this.init_game(player2, player1, display)

            running = True
            while running:
                this.display_board()
                result = this.take_turn()
                if result == 1:
                    this.display_board()
                    this.print(f"{this.curr_player.name} WINS\n")
                    this.curr_player.win()
                    this.next_player.lose()
                    running = False
                    break
                elif result == -1:
                    this.print(f"TIE GAME\n")
                    this.curr_player.tie()
                    this.next_player.tie()
                    running = False
                    break
                else:
                    this.switch_sides()
            n_games -= 1
            n_games_played += 1

def create_player(player_type):
    if player_type == "human":
        return HumanPlayer()
    elif player_type == "q":
       return QPlayer.load_from_checkpoint()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play tictactoe')
    parser.add_argument('-x', '--playerx', metavar='P1', type=str, help='Player 1 type', choices=['human', 'neat', 'q'], default='human', dest='p1')
    parser.add_argument('-o', '--playero', metavar='P2', type=str, help='Player 2 type', choices=['human', 'neat', 'q'], default='human', dest='p2')
    parser.add_argument('-n', metavar='N', type=int, help='Number of games (-1 for unlimited)', default=-1, dest='n')
    args = parser.parse_args()

    player1 = create_player(args.p1)
    player2 = create_player(args.p2)

    TicTacToe().play(player1, player2, n_games=args.n, display=True)




