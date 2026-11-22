# pylint: disable=unused-argument, duplicate-code
from typing import Sequence
from power_grid.simple_types import Resource, PlayerColor, PowerPlantNumber, RequestError


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

class InterfacePlayerBoardDeterminingPlayerOrder:
    def best_power_plant_number(self) -> PowerPlantNumber:
        """Returns the player's highest-numbered power plant."""
        raise NotImplementedError

    def number_of_connectable_cities(self) -> int:
        """Returns the number of cities the player can power with their resources."""
        raise NotImplementedError

    def outstanding_money(self) -> int:
        """Returns the player's available money."""
        raise NotImplementedError

class InterfaceTownsDeterminePlayerOrder:
    def get_number_of_houses(self, player: PlayerColor) -> int:
        """Returns the number of houses built by the player."""
        raise NotImplementedError

class InterfaceTownsCheckAndBumpStep:
    def get_max_number_of_houses(self) -> int:
        """Returns the largest number of houses owned by any player."""
        raise NotImplementedError

    def start_step_2(self) -> None:
        """Allow up to two players to build in each town."""
        raise NotImplementedError

    def start_step_3(self) -> None:
        """Allow up to three players to build in each town."""
        raise NotImplementedError

class InterfacePowerPlantMarketCheckAndBumpStep:
    def is_step_3_start(self) -> bool:
        """Return whether the Step 3 card has been drawn."""
        raise NotImplementedError

    def start_step_2(self) -> None:
        """Remove the smallest power plant and draw its replacement."""
        raise NotImplementedError

    def start_step_3(self) -> None:
        """Apply the Step 3 power plant market changes"""
        raise NotImplementedError
