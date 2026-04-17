from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

from ..models import Order, Card, CardPrices, Transaction


class Market(ABC):
    def __init__(
        self,
        name: str,
        sell_list: list[Order] | None = None,
        buy_list: list[Order] | None = None,
    ):
        self.name = name
        self.stock = {card: 0 for card in Card}
        self.prices = CardPrices(ROCK=0, PAPER=0, SCISSOR=0)
        self.buy_list: list[Order] | None = sell_list
        self.sell_list: list[Order] | None = buy_list
        self.executed_trades: list[Transaction] = []

    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass

    def get_prices(self) -> CardPrices:
        return self.prices

    @property
    def get_stock(self) -> dict:
        return self.stock

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def shuffleOrder(self) -> None:
        pass
