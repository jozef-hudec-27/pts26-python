# pylint: disable=unused-argument, duplicate-code
from typing import Sequence
from power_grid.simple_types import Resource, PlayerColor, RequestError


class InterfaceResourcePoolResourceMarket:
    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        assert False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        assert False

    def to_string(self) -> str:
        assert False

class InterfaceTownsBuildingHouses:
    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str], max_money: int
    ) -> int | RequestError:
        """Builds the requested houses and returns their total price.

        Return RequestError without changing houses if the request is invalid
        or exceeds max_money. The price includes houses and connections.
        """
        raise NotImplementedError

    def get_max_number_of_houses(self) -> int:
        """Returns the largest number of houses owned by any player."""
        raise NotImplementedError

class InterfacePlayerBoardBuildingHouses:
    def outstanding_money(self) -> int:
        """Returns the player's available money."""
        raise NotImplementedError

    def spend_money(self, amount: int) -> None:
        """Deducts a nonnegative amount within the player's available money."""
        raise NotImplementedError
