from games import Game, GameResultType

class GameOneCard(Game):

    def play(self) -> GameResultType:
        return GameResultType.TIE # TODO: implement function!