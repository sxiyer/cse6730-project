from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
from uuid import UUID
from pathlib import Path

##### Enums #####


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


class GameResultType(Enum):
    WIN = "win"  # somebody won
    LOSS = "loss"  # here for losers to know they lost
    TIE = "tie"  # tie


##### Data Classes #####


@dataclass
class Order:
    agent_UID: UUID  # We might not need it it!
    order_type: OrderType
    card_type: Card
    limit_price: float
    order_UID: UUID  # We might not need it!
    callback: Callable | None
    executed: bool | None
    agent_type: AgentType
    exchange_price: float = 0.0
    quantity: int = 1

    def __hash__(self):
        return hash(self.order_UID)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Order):
            return NotImplemented
        return self.order_UID == value.order_UID

    def __le__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return (self.limit_price, self.order_UID) < (other.limit_price, other.order_UID)


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
class TickSnapShot:
    tick: int
    card_prices: CardPrices
    order_volume: dict
    top_twenty_players: list[UUID]  # Sorted in decreasing order
    top_twenty_scalper: list[UUID]  # Sorted in decreasing order
    # TODO collect info by agent type e.i. the top performing scalper class


@dataclass(frozen=True)
class VizConfig:
    base_dir: Path = Path("results/plots")
