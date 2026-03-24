from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rich.layout import Layout

from .header import Header
from .home_screen import HomeScreen
from .footer import Footer
from .leader_board import LeaderBoard
from .match_results import MatchResults

import readchar


@dataclass
class SimulationContext:
    """Context for the simulation, holding all relevant state."""

    num_players: int = 2
    num_rounds: int = 1


class AppState(ABC):
    """Abstract base class for application states."""

    def __init__(self):
        self.initialized: bool = False

    @abstractmethod
    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the state."""
        pass

    @abstractmethod
    def render(self, layout: Layout, context: SimulationContext) -> Layout | None:
        """Render the state to the given layout."""
        pass

    def _build_home_layout(self, context: SimulationContext) -> Layout:
        """Build the initial home screen layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["header"].update(Header())
        layout["body"].update(HomeScreen(context.num_players, context.num_rounds))
        layout["footer"].update(Footer())
        return layout

    def _update_home_layout(self, layout: Layout, context: SimulationContext) -> Layout:
        """Update the home screen layout with new context values."""
        layout["body"].update(HomeScreen(context.num_players, context.num_rounds))
        return layout


class HomePlayerState(AppState):
    """State for the home screen player selection."""

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

    def render(self, layout: Layout, context: SimulationContext) -> Layout:
        if not self.initialized:
            self.initialized = True
            layout = self._build_home_layout(context)
        else:
            layout = self._update_home_layout(layout, context)
        return layout


class HomeRoundState(AppState):
    """State for the home screen round selection."""

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the home round state."""
        if key == " ":
            return RunningState()
        elif key == readchar.key.UP:
            context.num_rounds = min(
                context.num_rounds * 2, 2**10
            )  # Cap at 2^10 rounds
            return self
        elif key == readchar.key.DOWN:
            context.num_rounds = max(1, context.num_rounds // 2)
            return self
        elif key.lower() == "q":
            return None
        return self

    def render(self, layout: Layout, context: SimulationContext) -> Layout:
        if not self.initialized:
            self.initialized = True
            layout = self._build_home_layout(context)
        else:
            layout = self._update_home_layout(layout, context)
        return layout


class RunningState(AppState):
    """State for the main simulation running."""

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        if key.lower() == "q":
            return None
        return self  # No transitions from running state for now

    def render(self, layout: Layout) -> Layout:
        if not self.initialized:
            self.initialized = True
