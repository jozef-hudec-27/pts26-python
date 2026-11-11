from collections import Counter
from itertools import combinations
from typing import Sequence

from power_grid.simple_types import PowerPlant, Resource


class MaximumNumberOfUsablePowerPlants:
    def number_of_suppliable_towns(
        self, resources: Sequence[Resource], power_plants: Sequence[PowerPlant]
    ) -> int:
        """Returns the maximum towns supplied by any subset of given plants.

        resources is the complete available inventory. Left over fuel is allowed.
        Each plant can run at most once.
        """
        resource_counts = Counter(resources)
        maximum_towns = 0
        for size in range(1, len(power_plants) + 1):
            for selected_plants in combinations(power_plants, size):
                plant_numbers = {plant.number.number for plant in selected_plants}
                if len(plant_numbers) != len(selected_plants):
                    continue

                towns = sum(plant.number_of_cities for plant in selected_plants)
                if towns > maximum_towns and self._can_supply(resource_counts, selected_plants):
                    maximum_towns = towns

        return maximum_towns

    def _can_supply(
        self, resource_counts: Counter[Resource], power_plants: Sequence[PowerPlant]
    ) -> bool:
        for size in range(1, len(power_plants) + 1):
            for group in combinations(power_plants, size):
                required = sum(plant.resource_amount for plant in group)
                accepted_resources = {
                    resource for plant in group for resource in plant.accepted_resources
                }
                available = sum(resource_counts[resource] for resource in accepted_resources)
                if required > available:
                    return False

        return True
