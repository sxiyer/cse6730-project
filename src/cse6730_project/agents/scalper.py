from uuid import UUID

from .base import Agent


class Scalper(Agent):
    def __init__(self, uid: UUID, money: float = 0.0):
        super().__init__(uid, money)

    pass
