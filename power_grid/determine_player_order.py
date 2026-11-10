from typing import Sequence

from power_grid.simple_types import PlayerColor


class DeterminePlayerOrder:
    """Determines turn order and final ranking from player game state."""

    def reorder(self) -> Sequence[PlayerColor]:
        """Return players in the order used for the next game round.

        Players are ranked based on their number of built houses
        and their highest-numbered power plant.
        """
        raise NotImplementedError

    def game_result(self) -> Sequence[PlayerColor]:
        """Return the final ranking of players, from winner to last place.

        Rankings are determined by the number of powered cities,
        and remaining money as the tie-breaker.
        """
        raise NotImplementedError
