
# pylint: disable=unused-argument
from typing import Sequence


class Connections:
    def __init__(
        self, distances: Sequence[tuple[str, str, int]]
    ) -> None:
        """Creates a map of connections between towns.
        Each tuple contains two town names and their connection cost.
        Copies the provided distances.
        """
        self._distances: list[tuple[str, str, int]] = list(distances)

    def calculate_connecting_cost(
        self, from_towns: Sequence[str], to_towns: Sequence[str]
    ) -> int:
        """Returns the minimum cost of connecting the requested towns.

        from_towns: Towns already in the player's network.
        to_towns: Towns the player wants to connect.
        """
        raise NotImplementedError
