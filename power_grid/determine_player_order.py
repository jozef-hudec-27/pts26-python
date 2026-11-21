from typing import Sequence, Mapping

from power_grid.interfaces import (
    InterfacePlayerBoardDeterminingPlayerOrder,
    InterfaceTownsDeterminePlayerOrder,
)
from power_grid.simple_types import PlayerColor

class DeterminePlayerOrder:
    """Determines turn order and final ranking from player game state."""

    def __init__(
        self,
        towns: InterfaceTownsDeterminePlayerOrder,
        player_boards: Mapping[PlayerColor, InterfacePlayerBoardDeterminingPlayerOrder],
    ) -> None:
        self._towns = towns
        self._player_boards = dict(player_boards)

    def reorder(self) -> Sequence[PlayerColor]:
        """Return players in the order used for the next game round.

        Players are ranked based on their number of built houses
        and their highest-numbered power plant.
        """
        return sorted(
            self._player_boards,
            key=lambda player: (
                self._towns.get_number_of_houses(player),
                self._player_boards[player].best_power_plant_number().number,
            ),
            reverse=True,
        )

    def game_result(self) -> Sequence[PlayerColor]:
        """Return the final ranking of players, from winner to last place.

        Rankings are determined by the number of powered cities,
        and remaining money as the tie-breaker.
        """
        return sorted(
            self._player_boards,
            key=lambda player: (
                min(
                    self._towns.get_number_of_houses(player),
                    self._player_boards[player].number_of_connectable_cities(),
                ),
                self._player_boards[player].outstanding_money(),
            ),
            reverse=True,
        )
