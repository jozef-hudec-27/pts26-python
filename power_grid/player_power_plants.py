# pylint: disable=unused-argument
from typing import Sequence

from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


class PlayerPowerPlants:
    def __init__(
        self, power_plant_limit: int, power_plants: Sequence[PowerPlant] = ()
    ) -> None:
        """Creates a board with an explicit limit and optional initial plants.

        Copies the initial collection. Raise ValueError for a < 1 limit,
        repeated plant numbers or an initial collection over limit.
        """
        raise NotImplementedError

    def best_power_plant(self) -> PowerPlantNumber | None:
        """Returns the highest owned plant number, None if no plants are owned."""
        raise NotImplementedError

    def receive_power_plant(self, power_plant: PowerPlant) -> bool:
        """Adds a plant and returns whether the collection is within its limit

        False means the plant was added and one must now be removed.
        Raise ValueError for a repeated plant number or if another
        plant is received while already above the limit.
        """
        raise NotImplementedError

    def remove_power_plant(
        self, ppn: PowerPlantNumber, new_resources: Sequence[Resource]
    ) -> RequestError | None:
        """Removes owned plant if the remaining plants can store new_resources.

        new_resources is the full inventory remaining after proposed discards.
        Returns RequestError for an unowned plant or insufficient storage.
        Leaves state unchanged on error. Returns None on success. The caller
        owns the resource inventory and applies any actual fuel discards.
        """
        raise NotImplementedError

    def number_of_connectable_cities(self, resources: Sequence[Resource]) -> int:
        """Returns maximum towns supplied by owned plants with available fuel.

        resources is the full available inventory.
        """
        raise NotImplementedError

    def can_store_resources(self, resources: Sequence[Resource]) -> bool:
        """Checks if owned plants can store the full inventory."""
        raise NotImplementedError

    def use_power_plant(
        self, ppns: Sequence[PowerPlantNumber], resources_to_burn: Sequence[Resource]
    ) -> int | RequestError:
        """Returns towns supplied by running the selected owned plants once.

        Returns RequestError for unowned or repeated numbers or an invalid
        fuel allocation. The caller checks fuel ownership and consumes
        it after success.
        """
        raise NotImplementedError
