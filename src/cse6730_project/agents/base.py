from abc import ABC, abstractmethod
from random import random
from uuid import UUID

from ..models import Order, Card


class Agent(ABC):

    def __init__(self, uid: UUID, money: float = 0.0):
        self.UID: UUID = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}
        self.history: list = []

    @abstractmethod
    def buy_order(self) -> Order | None:
        pass

    @abstractmethod
    def sell_order(self) -> Order | None:
        pass
