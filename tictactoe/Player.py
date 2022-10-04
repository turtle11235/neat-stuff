import time

class Player:

    def __init__(this, name=None):
        this.name = name
        this.mark = None
        this.num_bad_moves = 0
        this.num_wins = 0
        this.num_losses = 0
        this.num_ties = 0
        this.num_games = 0

    def make_move(this, board, retry=False):
        if retry:
            this.num_bad_moves += 1
        return this._make_move(board, retry)
        
    def _make_move(this, board, retry):
        pass

    def win(this):
        this.num_wins += 1
        this.num_games += 1

    def lose(this):
        this.num_losses += 1
        this.num_games += 1

    def tie(this):
        this.num_ties += 1
        this.num_games += 1

class HumanPlayer(Player):

    def _make_move(this, *_):
        return int(input())

class AIPlayer(Player):

    def __init__(this, delay=0, name=None):
        super().__init__(name)
        this.delay = delay

    def make_move(this, board, retry=False):
        start = time.time()
        result = super().make_move(board, retry)
        time.sleep(max(this.delay - (time.time() - start), 0))
        return result