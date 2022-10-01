
from turtle import pos


board = [None, None, None, None, None, None, None, None, None]
marks = ['x', 'o']

def make_move(position, player):
    if (board[position] is None):
        board[position] = player
        return check_win()
    else:
        return -1

def check_win():
    winning_configurations = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
    for winning_configuration in winning_configurations:
        mark = board[winning_configuration[0]]
        for position in winning_configuration:
            if board[position] is None or board[position] != mark:
                break
        else:
            return 1
    else:
        return 0

def display_board(curr_player):
    print(f'''
    {player_to_mark(board[0])}|{player_to_mark(board[1])}|{player_to_mark(board[2])}
    -+-+-
    {player_to_mark(board[3])}|{player_to_mark(board[4])}|{player_to_mark(board[5])}
    -+-+-
    {player_to_mark(board[6])}|{player_to_mark(board[7])}|{player_to_mark(board[8])}

    Player {curr_player + 1}'s turn
    ''')

def player_to_mark(player):
    if player is None:
        return ' '
    elif player == 0:
        return 'x'
    else:
        return 'o'

def play(player1=None, player2=None):
    running = True
    player = 0
    while running:
        display_board(player)
        while True:
            position = int(input())
            if position >= 0 and position <= 8:
                res = make_move(position, player)
                if res == 1:
                    print(f"Player {player + 1} wins")
                    running = False
                    break
                elif res == 0:
                    player = (player + 1) % 2
                    break

if __name__ == "__main__":
    play()




