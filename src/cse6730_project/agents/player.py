from uuid import UUID
from ..utils import rng_rand
import random
from typing import Callable

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
    # TODO: Implement a generator function that will seed the player's deck that
    # can be swapped for different deck distribution functions. Use yielding to
    # track and specify different populations of players getting different
    # seeding functions for their decks
    def __init__(
        self,
        uid: UUID,
        seedDeck: Callable,
        money: float = 0.0,
    ):
        super().__init__(uid, money)
        card: Card = rng_rand.choice(list(Card))
        self.deck[card] += 1
