from Player import Player

class HumanPlayer(Player):

    def _make_move(this, *_):
        return int(input())