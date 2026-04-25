from abc import ABC, abstractmethod
import copy

from ..models import Order, Card, CardPrices


class Market(ABC):
    def __init__(
        self,
        name: str,
        sell_list: list[Order] | None = None,
        buy_list: list[Order] | None = None,
    ):
        self.name = name
        self.stock = {card: 0 for card in Card}
        self.prices = CardPrices(ROCK=0.0, PAPER=0.0, SCISSOR=0.0)
        self.buy_list: list[Order] | None = buy_list
        self.sell_list: list[Order] | None = sell_list

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass

    def get_prices(self) -> CardPrices:
        return copy.copy(self.prices)

    def get_stock(self) -> dict:
        return copy.copy(self.stock)

    def insert_orders(self, buy_orders: list[Order], sell_orders: list[Order]) -> None:
        self.buy_list = buy_orders
        self.sell_list = sell_orders

    def getBalance(self) -> dict:
        return {card: self.stock[card] * self.prices[card] for card in Card}

    def shuffleOrder(self) -> None:
        import random

        if self.buy_list:
            random.shuffle(self.buy_list)
        if self.sell_list:
            random.shuffle(self.sell_list)
