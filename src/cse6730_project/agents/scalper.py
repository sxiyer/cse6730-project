from uuid import UUID

from .base import Agent


class Scalper(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)

    def wake_up_agent(self) -> None:
        pass

    def buy_order(self) -> None:
        return None

    def sell_order(self) -> None:
        return None
