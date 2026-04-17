from uuid import UUID
from ..utils import rng_rand
import random

from .base import Agent
from ..models import Card, PlayerBehavior, CardPrices, Order


class Player(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE

    def shuffleDeck(self) -> list[Card]:
        cards = []

        for card, count in self.deck.items():
            cards.extend([card] * count)

        random.shuffle(cards)

        return cards

    def buy_order(self, card_prices: CardPrices) -> Order | None:
        return None

    def sell_order(self, card_prices: CardPrices) -> Order | None:
        return None


class PlayerOneCard(Player):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)
        card: Card = rng_rand.choice(list(Card))
        self.deck[card] += 1
