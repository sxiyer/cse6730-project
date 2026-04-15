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
        self.pending_orders: list[Order] = []

    @abstractmethod
    def wake_up_agent(self) -> None:
        # TODO: Pass in the current values of cards from the market. 
        pass

    @abstractmethod
    def buy_order(self) -> Order | None:
        pass

    @abstractmethod
    def sell_order(self) -> Order | None:
        pass
