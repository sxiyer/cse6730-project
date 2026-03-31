from dataclasses import dataclass
from enum import Enum
import uuid


class Card(Enum):
    Rock = "R"
    Paper = "P"
    Scissor = "S"


class TypeExchanges(Enum):
    Sell = "Sell"
    Buy = "Buy"


@dataclass
class CardValues:
    rock: float
    paper: float
    scissor: float


@dataclass
class Order:
    agent_uid: uuid.UUID
    tick: int
    card_type: Card
    order_type: TypeExchanges
    limit_price: float
