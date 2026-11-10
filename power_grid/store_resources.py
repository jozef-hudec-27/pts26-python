from collections import Counter
from itertools import combinations
from typing import Sequence

from power_grid.simple_types import PowerPlant, Resource


class StoreResources:
    def can_store_resources(
        self, resources: Sequence[Resource], power_plants: Sequence[PowerPlant]
    ) -> bool:
        """Checks whether all given resources can be stored in supplied plants."""
        resource_counts = Counter(resources)

        for size in range(1, len(resource_counts) + 1):
            for group in combinations(resource_counts, size):
                required = sum(resource_counts[resource] for resource in group)
                capacity = sum(
                    2 * plant.resource_amount
                    for plant in power_plants
                    if any(resource in plant.accepted_resources for resource in group)
                )

                if required > capacity:
                    return False

        return True
