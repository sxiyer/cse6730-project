from dataclasses import dataclass
from enum import Enum, auto
import uuid


class Cards(Enum):
    Rock = auto()
    Paper = auto()
    Scissor = auto()


class TypeExhanges(Enum):
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
    cardType: Cards
    orderType: TypeExhanges
