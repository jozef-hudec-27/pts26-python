from collections import Counter
from itertools import combinations
from typing import Sequence

from power_grid.simple_types import PowerPlant, RequestError, Resource


class UsePowerPlants:
    def number_of_suppliable_towns(
        self, resources: Sequence[Resource], power_plants: Sequence[PowerPlant]
    ) -> int | RequestError:
        """Returns towns supplied by running every given plant once.

        resources is the exact fuel to burn. Returns RequestError
        if fuel cannot be allocated to run all selected plants, fuel
        is left over, or a plant number is repeated.
        """
        plant_numbers = [plant.number.number for plant in power_plants]
        if len(plant_numbers) != len(set(plant_numbers)):
            return RequestError("Repeated power plant number.")

        total_fuel_required = sum(plant.resource_amount for plant in power_plants)
        if len(resources) != total_fuel_required:
            return RequestError("Resource amount does not match plants' requirements exactly.")

        fuel_counts = Counter(resources)
        for group_size in range(1, len(fuel_counts) + 1):
            for fuel_group in combinations(fuel_counts, group_size):
                fuel_amount = sum(fuel_counts[resource] for resource in fuel_group)
                compatible_requirement = sum(
                    plant.resource_amount
                    for plant in power_plants
                    if any(resource in plant.accepted_resources for resource in fuel_group)
                )
                if fuel_amount > compatible_requirement:
                    return RequestError("The fuel cannot run all selected power plants.")

        return sum(plant.number_of_cities for plant in power_plants)
