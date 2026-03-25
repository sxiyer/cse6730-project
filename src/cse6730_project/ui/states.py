from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

import readchar

from rich.layout import Layout

from .layouts import Header, Footer, HomeScreen, LeaderBoard, MatchResults, BasicLayout


@dataclass
class SimulationContext:
    """Context for the simulation, holding all relevant state."""

    num_players: int = 2
    step_size: int = 1


class AppState(ABC):
    """Abstract base class for application states."""

    def __init__(self):
        self.initialized: bool = False

    @abstractmethod
    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the state."""
        pass

    @abstractmethod
    def render(self, layout: Layout, context: SimulationContext) -> Layout:
        """Render the state to the given layout."""
        pass

    def _build_layout(
        self,
        context: SimulationContext,
        template_layout: BasicLayout | None = None,
        multi_layout: tuple[BasicLayout, BasicLayout] | None = None,
    ) -> Layout:
        """Build the initial screen layout."""
        assert not (
            template_layout and multi_layout
        ), "Cannot provide both template and multi layouts"
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["header"].update(Header())
        if template_layout is not None:
            layout["body"].update(template_layout)
        elif multi_layout is not None:
            layout["body"].split_row(
                Layout(name="leaderboard"),
                Layout(name="match_results"),
            )
            layout["leaderboard"].update(multi_layout[0])
            layout["match_results"].update(multi_layout[1])
        layout["footer"].update(Footer())
        return layout

    def _update_layout(
        self,
        layout: Layout,
        context: SimulationContext,
        template_layout: BasicLayout | None = None,
        multi_layout: tuple[BasicLayout, BasicLayout] | None = None,
    ) -> Layout:
        """Update the screen layout with new context values."""
        assert not (
            template_layout and multi_layout
        ), "Cannot provide both template and multi layouts"
        if template_layout is not None:
            layout["body"].update(template_layout)
        elif multi_layout is not None:
            layout["leaderboard"].update(multi_layout[0])
            layout["match_results"].update(multi_layout[1])
        return layout


class HomeState(AppState):
    """Base state for the home screen."""

    def __init__(self):
        super().__init__()

    def render(self, layout: Layout, context: SimulationContext) -> Layout:
        if not self.initialized:
            self.initialized = True
            layout = self._build_layout(
                context, HomeScreen(context.num_players, context.step_size)
            )
        else:
            layout = self._update_layout(
                layout, context, HomeScreen(context.num_players, context.step_size)
            )
        return layout


class HomePlayerState(HomeState):
    """State for the home screen player selection."""

    def __init__(self):
        super().__init__()

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the home player state."""
        if key == " ":
            return HomeStepSize()
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


class HomeStepSize(HomeState):
    """State for the home screen round selection."""

    def __init__(self):
        super().__init__()

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        """Handle input for the home round state."""
        if key == " ":
            return RunningState()
        elif key == readchar.key.UP:
            context.step_size = min(context.step_size * 2, 2**10)  # Cap at 2^10 rounds
            return self
        elif key == readchar.key.DOWN:
            context.step_size = max(1, context.step_size // 2)
            return self
        elif key.lower() == "q":
            return None
        return self


class RunningState(AppState):
    """State for the main simulation running."""

    def __init__(self):
        super().__init__()

    def handle_input(self, key: str, context: SimulationContext) -> AppState | None:
        if key.lower() == "q":
            return None
        return self  # No transitions from running state for now

    def render(self, layout: Layout, context: SimulationContext) -> Layout:
        if not self.initialized:
            self.initialized = True
            layout = self._build_layout(
                context, multi_layout=(LeaderBoard(), MatchResults())
            )
        else:
            layout = self._update_layout(
                layout, context, multi_layout=(LeaderBoard(), MatchResults())
            )
        return layout
