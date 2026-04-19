from .base import Game, GameResultType
from ..utils import logger


class GameOneCard(Game):
    def play(self) -> GameResultType:
        player1 = self.player1
        player2 = self.player2

        cards1 = self.player1.shuffleDeck()
        cards2 = self.player2.shuffleDeck()

        card1 = cards1.pop()
        card2 = cards2.pop()

        result: GameResultType = self.resolveRPS((player1, card1), (player2, card2))

        if result == GameResultType.WIN and self.winner and self.loser:
            logger.debug(
                f"Player {player1.UID} Plays {card1} vs Player {player2.UID} plays {card2}, Player {self.winner.UID} Wins!"
            )
            self.winner.update_game_results(GameResultType.WIN)
            self.loser.update_game_results(GameResultType.LOSS)
        elif self.winner and self.loser:
            self.winner.update_game_results(GameResultType.TIE)
            self.loser.update_game_results(GameResultType.TIE)

        self.result = result
        self.rounds_played += 1

        return result
