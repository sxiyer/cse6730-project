from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

from ..models import Order, Card


class Market(ABC):
    def __init__(
        self,
        name: str,
        player_info: dict[UUID, Any] | None = None,
        scalper_info: dict[UUID, Any] | None = None,
        game_pairs: list | None = None,
        sell_list: list | None = None,
        buy_list: list | None = None,
    ):
        self.player_info = player_info
        self.scalper_info = scalper_info
        self.game_pairs = game_pairs
        self.sell_list = sell_list
        self.buy_list = buy_list
        self.name = name
        self.stock = {card: 0 for card in Card}
        self.prices = {card: 0.0 for card in Card}
        self.buy_list: list[Order] = []
        self.sell_list: list[Order] = []
        self.executed_trades: list[Order] = []

    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass

    @property
    def get_prices(self) -> dict:
        return self.prices

    @property
    def get_stock(self) -> dict:
        return self.stock

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def execute_trade(self) -> None:
        pass

    @abstractmethod
    def getBalance(self) -> None:
        pass

    @abstractmethod
    def shuffleOrder(self) -> None:
        pass
