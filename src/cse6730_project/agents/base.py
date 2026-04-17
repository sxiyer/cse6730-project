from abc import ABC, abstractmethod
from typing import Callable
from random import random
from uuid import UUID

from ..models import Order, Card, OrderType, CardPrices


class Agent(ABC):

    def __init__(self, uid: UUID, money: float = 0.0):
        self.UID: UUID = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}
        self.history: list = []
        self.pending_orders: list[Order] = []

    def wake_up_agent(self, card_prices: CardPrices) -> Callable:
        """The function takes in the current value of all three cards
        and returns a function to allow the simulation to update the
        agent's deck and money"""

        buy_order = self.buy_order(card_prices)
        sell_order = self.sell_order(card_prices)

        def update_agent(successful: bool, exchanged_prices: dict[Card, float]) -> None:
            if successful and buy_order:
                self.deck[buy_order.card_type] -= buy_order.quantity
                self.money -= exchanged_prices[buy_order.card_type] * buy_order.quantity
            if successful and sell_order:
                self.deck[sell_order.card_type] += sell_order.quantity
                self.money += (
                    exchanged_prices[sell_order.card_type] * sell_order.quantity
                )

        return update_agent

    @abstractmethod
    def buy_order(self, card_prices: CardPrices) -> Order | None:
        pass

    @abstractmethod
    def sell_order(self, card_prices: CardPrices) -> Order | None:
        pass
