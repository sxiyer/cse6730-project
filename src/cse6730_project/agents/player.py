from uuid import UUID
import random

from .base import Agent
from ..models import Card


class Player(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)

    def shuffleDeck(self) -> list[Card]:
        cards = []

        for card, count in self.deck.items():
            cards.extend([card] * count)

        random.shuffle(cards)

        return cards

    def wake_up_agent(self) -> None:
        self.pending_orders = []
        buy = self.buy_order()
        sell = self.sell_order()
        if buy:
            self.pending_orders.append(buy)
        if sell:
            self.pending_orders.append(sell)

    def buy_order(self) -> None:
        return None

    def sell_order(self) -> None:
        return None
