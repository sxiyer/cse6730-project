from base import Agent

from ..models import Order


class Player(Agent):

    def buy_order(self) -> Order | None:
        pass

    def sell_order(self) -> Order | None:
        pass
