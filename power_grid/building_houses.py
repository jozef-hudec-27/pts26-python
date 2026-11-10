# pylint: disable=unused-argument
from typing import Sequence

from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError


class BuildingHouses:
    """Coordinates the players' turns during the house-building phase."""

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Start a new building phase with the given player turn order."""
        raise NotImplementedError

    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str]
    ) -> PhaseStatus | RequestError:
        """Process a player's request to build houses in the named towns.

        Return RequestError for an invalid request; otherwise return the
        phase status to indicate whether building continues or ends.
        """
        raise NotImplementedError

    def get_state(self) -> str:
        """Return a string describing the current house-building phase."""
        raise NotImplementedError
