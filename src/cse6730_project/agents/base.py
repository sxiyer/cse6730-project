from abc import ABC, abstractmethod
from uuid import UUID

from ..models import Order, Card, CardPrices


class Agent(ABC):

    def __init__(self, uid: UUID, money: float = 0.0):
        self.UID: UUID = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}

    @abstractmethod
    def wake_up_agent(self, card_prices: CardPrices) -> tuple[list[Order], list[Order]]:
        pass
