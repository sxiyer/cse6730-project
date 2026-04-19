from abc import ABC, abstractmethod
from typing import Callable
from uuid import UUID

from ..models import Order, Card, CardPrices


class Agent(ABC):

    def __init__(self, uid: UUID, money: float = 0.0):
        self.UID: UUID = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}

    def wake_up_agent(
        self, card_prices: CardPrices
    ) -> tuple[Order | None, Order | None, Callable] | None:
        """The function takes in the current value of all three cards
        and returns a function to allow the simulation to update the
        agent's deck and money"""

        buy_order = self.buy_order(card_prices)
        sell_order = self.sell_order(card_prices)

        def update_agent(successful: bool, exchanged_prices: dict[Card, float]) -> None:
            if successful and buy_order:
                self.deck[buy_order.card_type] += buy_order.quantity
                self.money -= exchanged_prices[buy_order.card_type] * buy_order.quantity
            if successful and sell_order:
                self.deck[sell_order.card_type] -= sell_order.quantity
                self.money += (
                    exchanged_prices[sell_order.card_type] * sell_order.quantity
                )

        if self.buy_order and self.sell_order:
            return (buy_order, sell_order, update_agent)
        # The agent won't participate
        return None

    @abstractmethod
    def buy_order(self, card_prices: CardPrices) -> Order | None:
        pass

    @abstractmethod
    def sell_order(self, card_prices: CardPrices) -> Order | None:
        pass
