from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class Card(Enum):
    ROCK = "R"
    PAPER = "P"
    SCISSOR = "S"


class Cards(Enum):
    ROCK: float
    PAPER: float
    SCISSOR: float

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    agent_UID: UUID 
    order_type: OrderType
    card_type: Card
    limit_price: float
    quantity: int = 1
