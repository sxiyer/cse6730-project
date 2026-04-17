from .base import Game, GameResultType
from ..agents import Player
from ..utils import logger

class GameOneCard(Game):
    def play(self) -> GameResultType:
        player1 = self.player1
        player2 = self.player2
        
        cards1 = self.player1.shuffleDeck()
        cards2 = self.player2.shuffleDeck()

        card1 = cards1.pop()
        card2 = cards2.pop()
        
        result: GameResultType = self.resolveRPS((player1, card1), (player2,card2))
        
        if result == GameResultType.WIN:
            logger.debug(f"Player {player1.UID} Plays {card1} vs Player {player2.UID} plays {card2}, Player {self.winner.UID} Wins!")
            self.winner.history.append(GameResultType.WIN)
            self.loser.history.append(GameResultType.LOSS)
        else:
            player1.history.append(GameResultType.TIE)
            player2.history.append(GameResultType.TIE)

        self.result = result
        self.rounds_played += 1
        
        return result