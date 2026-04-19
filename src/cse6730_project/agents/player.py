from typing import Callable
from uuid import UUID
import random

from .base import Agent
from ..utils import rng_rand
from ..models import Card, PlayerBehavior, CardPrices, Order, GameResultType


class Player(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE
        self.game_history: list[GameResultType] = []

    def shuffleDeck(self) -> list[Card]:
        cards = []

        for card, count in self.deck.items():
            cards.extend([card] * count)

        random.shuffle(cards)

        return cards

    def update_game_results(self, result: GameResultType) -> None:
        """Returns a function to update the agent on the result of the game"""
        self.game_history.append(result)

    def get_game_results(self) -> list[GameResultType]:
        return self.game_history

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        return None

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        return None


class PlayerOneCard(Player):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        card: Card = rng_rand.choice(list(Card))
        self.deck[card] += 1
