from dataclasses import dataclass
from enum import Enum, auto
import uuid


class Card(Enum):
    Rock = "R"
    Paper = "P"
    Scissor = "S"


class TypeExchanges(Enum):
    sell = auto()
    buy = auto()


@dataclass
class CardValues:
    rock: float
    paper: float
    scissor: float


@dataclass
class Order:
    agent_uid: uuid.UUID
    tick: int
    cardType: Card
    orderType: TypeExchanges
    limitPrice: float
