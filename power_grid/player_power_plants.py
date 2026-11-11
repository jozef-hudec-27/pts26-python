# pylint: disable=unused-argument
from typing import Sequence

from power_grid.maximum_number_of_usable_power_plants import MaximumNumberOfUsablePowerPlants
from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource
from power_grid.store_resources import StoreResources
from power_grid.use_power_plants import UsePowerPlants


class PlayerPowerPlants:
    def __init__(
        self, power_plant_limit: int, power_plants: Sequence[PowerPlant] = ()
    ) -> None:
        """Creates a board with an explicit limit and optional initial plants.

        Copies the initial collection. Raise ValueError for a < 1 limit,
        repeated plant numbers or an initial collection over limit.
        """
        if power_plant_limit < 1:
            raise ValueError("Power plant limit must be positive.")
        plant_numbers = [plant.number.number for plant in power_plants]
        if len(plant_numbers) != len(set(plant_numbers)):
            raise ValueError("Power plant numbers must be unique.")
        if len(power_plants) > power_plant_limit:
            raise ValueError("The initial power plant set is too large.")

        self._power_plant_limit = power_plant_limit
        self._power_plants = list(power_plants)

    def best_power_plant(self) -> PowerPlantNumber | None:
        """Returns the highest owned plant number, None if no plants are owned."""
        if not self._power_plants:
            return None

        best_plant = max(self._power_plants, key=lambda plant: plant.number.number)
        return best_plant.number

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
        return MaximumNumberOfUsablePowerPlants().number_of_suppliable_towns(
            resources, self._power_plants
        )

    def can_store_resources(self, resources: Sequence[Resource]) -> bool:
        """Checks if owned plants can store the full inventory."""
        return StoreResources().can_store_resources(resources, self._power_plants)

    def use_power_plant(
        self, ppns: Sequence[PowerPlantNumber], resources_to_burn: Sequence[Resource]
    ) -> int | RequestError:
        """Returns towns supplied by running the selected owned plants once.

        Returns RequestError for unowned or repeated numbers or an invalid
        fuel allocation. The caller checks fuel ownership and consumes
        it after success.
        """
        owned_plants = {plant.number.number: plant for plant in self._power_plants}
        selected_plants: list[PowerPlant] = []
        for ppn in ppns:
            plant = owned_plants.get(ppn.number)
            if plant is None:
                return RequestError(f"Power plant {ppn.number} is not owned.")
            selected_plants.append(plant)

        return UsePowerPlants().number_of_suppliable_towns(resources_to_burn, selected_plants)
