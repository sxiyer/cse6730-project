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

        result: GameResultType = self.resolveRPS((player1, card1), (player2, card2))

        if result == GameResultType.WIN:
            logger.debug(
                f"Player {player1.UID} Plays {card1} vs Player {player2.UID} plays {card2}, Player {self.winner.UID} Wins!"
            )
            self.winner.history.append(GameResultType.WIN)
            self.loser.history.append(GameResultType.LOSS)
        else:
            player1.history.append(GameResultType.TIE)
            player2.history.append(GameResultType.TIE)

        self.result = result
        self.rounds_played += 1

        return result


class GameNineCard(Game):
    def play(self) -> GameResultType:
        player1 = self.player1
        player2 = self.player2

        cards1 = player1.shuffleDeck()
        cards2 = player2.shuffleDeck()

        wins1 = 0
        wins2 = 0

        while cards1 and cards2:
            card1 = cards1.pop()
            card2 = cards2.pop()
            self.rounds_played += 1

            round_result = self.resolveRPS((player1, card1), (player2, card2))

            if round_result == GameResultType.WIN:
                if self.winner is player1:
                    wins1 += 1
                else:
                    wins2 += 1

                logger.debug(
                    f"Round {self.rounds_played}: "
                    f"P{player1.UID} plays {card1} vs P{player2.UID} plays {card2} "
                    f"— P{self.winner.UID} wins round ({wins1}-{wins2})"
                )

                if wins1 == 3 or wins2 == 3:
                    break
            else:
                logger.debug(
                    f"Round {self.rounds_played}: "
                    f"P{player1.UID} plays {card1} vs P{player2.UID} plays {card2} "
                    f"— Tie, both discarded ({wins1}-{wins2})"
                )

        if wins1 == 3 or wins2 == 3:
            # self.winner/loser already set by the final resolveRPS call
            self.winner.history.append(GameResultType.WIN)
            self.loser.history.append(GameResultType.LOSS)
            logger.debug(f"Game over: P{self.winner.UID} wins ({wins1}-{wins2})")
            self.result = GameResultType.WIN
        else:
            # deck exhaustion before either player reached 3
            self.winner = None
            self.loser = None
            player1.history.append(GameResultType.TIE)
            player2.history.append(GameResultType.TIE)
            logger.debug(f"Game over: Draw by exhaustion ({wins1}-{wins2})")
            self.result = GameResultType.TIE

        return self.result
