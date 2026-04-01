from abc import ABC, abstractmethod
from uuid import UUID

from ..models import Order


class Agent(ABC):

    def __init__(self):
        self.deck = list()
        self.money: int = 0
        self.id: UUID

    @abstractmethod
    def buy_order(self) -> Order | None:
        pass

    @abstractmethod
    def sell_order(self) -> Order | None:
        pass
