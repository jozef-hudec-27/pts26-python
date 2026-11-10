# pylint: disable=unused-argument
from typing import Sequence

from power_grid.simple_types import PowerPlant, Resource


class StoreResources:
    def can_store_resources(
        self, resources: Sequence[Resource], power_plants: Sequence[PowerPlant]
    ) -> bool:
        """Checks whether all given resources can be stored in supplied plants."""
        raise NotImplementedError
