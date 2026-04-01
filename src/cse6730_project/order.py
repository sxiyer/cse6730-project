from dataclasses import dataclass
from enum import Enum
from cards import Card

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    agent_UID: int
    order_type: OrderType
    card_type: Card
    limit_price: float
    quantity: int = 1