# pylint: disable=unused-argument
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
        raise NotImplementedError
