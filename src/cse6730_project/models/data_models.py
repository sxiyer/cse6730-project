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


class FitnessModes(Enum):
    EXPECTED = "expected"
    EMPERICAL = "emperical"


##### Data Classes #####


@dataclass
class GameResult:
    GameResultValue: GameResultType
    winner_UID: UUID
    loser_UID: UUID


@dataclass
class Order:
    agent_UID: UUID  # We might not need it it!
    order_type: OrderType
    card_type: Card
    limit_price: float
    order_UID: UUID | None  # We might not need it!
    callback: Callable | None
    executed: bool | None
    exchange_price: float = 0.0
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
class TickSnapShot:
    tick: int
    card_populations: dict  # dict[Card, float]
    card_prices: CardPrices | None = None
    order_volume: dict | None = None
    top_twenty_players: list[UUID] = field(default_factory=list)
    top_twenty_scalper: list[UUID] = field(default_factory=list)


@dataclass(frozen=True)
class VizConfig:
    base_dir: Path = Path("results/plots")
