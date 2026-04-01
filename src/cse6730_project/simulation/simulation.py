from abc import ABC, abstractmethod

from ..models import CardValues


class Simulation(ABC):

    def __init__(
        self,
        market,
        players: list,
        scalper: list,
    ):
        self.market = market
        self.players = players
        self.scalper = scalper

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def get_card_value(self) -> CardValues:
        pass
