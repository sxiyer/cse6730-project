from abc import ABC, abstractmethod
from uuid import UUID

from ..models import Order, Card, CardPrices, AgentType


class Agent(ABC):
    def __init__(self, uid: UUID, agent_type: AgentType, money: float = 0.0):
        self.UID: UUID = uid
        self.money: float = money
        self.deck: dict[Card, int] = {card: 0 for card in Card}
        self.agent_type = agent_type

    @abstractmethod
    def wake_up_agent(self, card_prices: CardPrices) -> tuple[list[Order], list[Order]]:
        pass
