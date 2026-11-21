from typing import Sequence,Mapping

from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError

from power_grid.interfaces import (
    InterfacePlayerBoardBuildingHouses,
    InterfaceTownsBuildingHouses,
)

class BuildingHouses:
    """Coordinates the players' turns during the house-building phase."""

    def __init__(
        self,
        towns: InterfaceTownsBuildingHouses,
        player_boards: Mapping[PlayerColor, InterfacePlayerBoardBuildingHouses],
    ) -> None:
        """Creates a building phase for two to six players.

        Copies the player mapping while sharing the towns and player boards.
        Raise ValueError for an unsupported number of players.
        """
        game_end_thresholds = {2: 18, 3: 17, 4: 17, 5: 15, 6: 14}

        if len(player_boards) not in game_end_thresholds:
            raise ValueError("The game requires two to six players.")

        self._towns = towns
        self._player_boards = dict(player_boards)
        self._game_end_threshold = game_end_thresholds[len(player_boards)]
        self._remaining_players: list[PlayerColor] = []
        self._status: PhaseStatus | None = None

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        """Start a new building phase with the given player turn order."""
        if self._status == PhaseStatus.PHASE_CONTINUES:
            raise ValueError("Cannot start a new phase while the current phase continues.")

        if self._status == PhaseStatus.GAME_ENDS:
            raise ValueError("Cannot start a new phase after the game has ended.")

        if (
            len(player_order) != len(self._player_boards)
            or set(player_order) != set(self._player_boards)
        ):
            raise ValueError("Player order must contain every player exactly once.")

        self._remaining_players = list(player_order)
        self._status = PhaseStatus.PHASE_CONTINUES

    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str]
    ) -> PhaseStatus | RequestError:
        """Process a player's request to build houses in the named towns.

        Return RequestError for an invalid request; otherwise return the
        phase status to indicate whether building continues or ends.
        """
        if self._status != PhaseStatus.PHASE_CONTINUES:
            return RequestError("The building phase is not active.")

        if player != self._remaining_players[-1]:
            return RequestError("It is not this player's turn.")

         # An empty request passes the turn without buying or spending anything.
        if town_names:
            board = self._player_boards[player]
            cost = self._towns.buy_houses(
                player, town_names, board.outstanding_money()
            )

            if isinstance(cost, RequestError):
                return cost

            board.spend_money(cost)

        self._remaining_players.pop()

        if self._remaining_players:
            return PhaseStatus.PHASE_CONTINUES

        if self._towns.get_max_number_of_houses() >= self._game_end_threshold:
            self._status = PhaseStatus.GAME_ENDS
        else:
            self._status = PhaseStatus.PHASE_ENDS

        return self._status

    def get_state(self) -> str:
        """Return a string describing the current house-building phase."""
        status = self._status.name if self._status is not None else "NOT_STARTED"

        current_player = (
            self._remaining_players[-1].name if self._remaining_players else "None"
        )
        remaining_players = ", ".join(
            player.name for player in reversed(self._remaining_players)
        ) or "None"

        return (
            f"Status: {status}\n"
            f"Current player: {current_player}\n"
            f"Remaining players: {remaining_players}"
        )
