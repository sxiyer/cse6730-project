from uuid import UUID
from ..utils import rng_rand
from typing import Callable
import random

from .base import Agent
from ..models import Card, PlayerBehavior, CardPrices, Order
from .seeding import seed_single_random

SeedFunction = Callable[[dict[Card, int]], None]


class Player(Agent):
    # TODO: Implement a generator function that will seed the player's deck that
    # can be swapped for different deck distribution functions. Use yielding to
    # track and specify different populations of players getting different
    # seeding functions for their decks
    def __init__(
        self,
        uid: UUID,
        money: float = 0.0,
        seed_deck: SeedFunction = seed_single_random,
    ):
        super().__init__(uid, money)
        self.PlayerBehavior: PlayerBehavior = PlayerBehavior.NONE
        self._seed_fn = seed_deck
        seed_deck(self.deck)

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
