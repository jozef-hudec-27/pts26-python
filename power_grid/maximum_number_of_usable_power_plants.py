# pylint: disable=unused-argument
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
        raise NotImplementedError
