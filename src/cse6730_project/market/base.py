from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

from ..models import Order


class Market(ABC):
    def __init__(
        self,
        player_info: dict[UUID, Any],
        scalper_info: dict[UUID, Any],
        game_pairs: list,
        sell_list: list,
        buy_list: list,
    ):
        self.player_info = player_info
        self.scalper_info = scalper_info
        self.game_pairs = game_pairs
        self.sell_list = sell_list
        self.buy_list = buy_list

    @abstractmethod
    def submit_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def execute_trade(self) -> None:
        pass

    @abstractmethod
    def getBalance(self):
        pass

    @abstractmethod
    def shuffleOrder(self) -> None:
        pass
