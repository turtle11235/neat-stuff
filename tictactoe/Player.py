
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


