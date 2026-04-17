from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

from ..models import Order, Card, CardValues


class Market(ABC):
    def __init__(
        self,
        name: str,
        player_info: dict[UUID, Any] | None = None,
        scalper_info: dict[UUID, Any] | None = None,
        game_pairs: list | None = None,
        sell_list: list[Order] | None = None,
        buy_list: list[Order] | None = None,
    ):
        self.player_info = player_info
        self.scalper_info = scalper_info
        self.game_pairs = game_pairs
        self.name = name
        self.stock = {card: 0 for card in Card}
        self.prices = CardValues(ROCK=0, PAPER=0, SCISSOR=0)
        self.buy_list: list[Order] | None = sell_list
        self.sell_list: list[Order] | None = buy_list
        self.executed_trades: list[Order] = []

    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass

    def get_prices(self) -> CardValues:
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
