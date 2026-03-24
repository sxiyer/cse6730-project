from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

import readchar


@dataclass
class SimulationContext:
    """Context for the simulation, holding all relevant state."""

    num_players: int = 2
    num_rounds: int = 1


class AppState(ABC):
    """Abstract base class for application states."""

    @abstractmethod
    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the state."""
        pass


class HomePlayerState(AppState):
    """State for the home screen player selection."""

    def __init__(self):
        pass

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the home player state."""
        if key == " ":
            return HomeRoundState()
        elif key == readchar.key.UP:
            context.num_players = min(
                context.num_players * 2, 2**20
            )  # Cap at 2^20 players
            return self
        elif key == readchar.key.DOWN:
            context.num_players = max(2, context.num_players // 2)
            return self
        elif key.lower() == "q":
            return None
        return self


class HomeRoundState(AppState):
    """State for the home screen round selection."""

    def __init__(self):
        pass

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the home round state."""
        if key == " ":
            return RunningState()
        elif key == readchar.key.UP:
            context.num_rounds *= 2
            return self
        elif key == readchar.key.DOWN:
            context.num_rounds = max(1, context.num_rounds // 2)
            return self
        elif key.lower() == "q":
            return None
        return self


class RunningState(AppState):
    """State for the main simulation running."""

    def __init__(self):
        pass

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        if key.lower() == "q":
            return None
        return self  # No transitions from running state for now
