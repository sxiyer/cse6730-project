from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class Card(Enum):
    ROCK = "R"
    PAPER = "P"
    SCISSOR = "S"


class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"


class AgentType(Enum):
    ALL = "all"
    PLAYER = "player"
    SCALPER = "scalper"


class PlayerBehavior(Enum):
    NONE = None  # No special behaviors
    COPYCAT = "copycat"
    MUTATOR = "mutator"


@dataclass
class Order:
    agent_UID: UUID
    order_type: OrderType
    card_type: Card
    limit_price: float
    quantity: int = 1


@dataclass
class CardPrices:
    ROCK: float
    PAPER: float
    SCISSOR: float

    def __getitem__(self, card: Card) -> float:
        match card:
            case Card.ROCK:
                return self.ROCK
            case Card.PAPER:
                return self.PAPER
            case Card.SCISSOR:
                return self.SCISSOR
            case _:
                raise KeyError(f"Invalid card type: {card}")


@dataclass(frozen=True)
class TimeConfig:
    start: int
    end: int
    step: int = 0


@dataclass(frozen=True)
class OdeConfig:
    z: float
    mu: float
    t_interval: TimeConfig
    t_eval: TimeConfig


@dataclass
class Transaction:
    agent_UID: UUID
    successful: bool


@dataclass
class TickSnapShot:
    tick: int
    card_prices: CardPrices
    order_volume: int
    top_twenty_players: list[UUID]
    top_twenty_scalper: list[UUID]
