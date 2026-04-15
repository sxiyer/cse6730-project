from uuid import UUID

from ..models import Order
from .base import Agent


class Scalper(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)

    def wake_up_agent(self) -> None:
        self.pending_orders = []
        buy = self.buy_order()
        sell = self.sell_order()
        if buy:
            self.pending_orders.append(buy)
        if sell:
            self.pending_orders.append(sell)

    def buy_order(self) -> Order | None:
        pass

    def sell_order(self) -> Order | None:
        pass 
