from power_grid.interfaces import (
    InterfaceTownsCheckAndBumpStep,
    InterfacePowerPlantMarketCheckAndBumpStep
)
from power_grid.resource_market import ResourceMarket

class CheckAndBumpStep:
    """Tracks the current game step and handles step changes."""

    def __init__(
            self,
            number_of_players: int,
            towns: InterfaceTownsCheckAndBumpStep,
            power_plant_market: InterfacePowerPlantMarketCheckAndBumpStep,
            resource_market: ResourceMarket,
        ) -> None:
        """Starts the game in Step 1."""
        if not 2 <= number_of_players <= 6:
            raise ValueError("The game requires 2-6 players")

        self.step: int = 1
        self._towns = towns
        self._power_plant_market = power_plant_market
        self._resource_market = resource_market
        self._step_2_threshold = 6 if number_of_players == 6 else 7

    def get_step(self) -> int:
        """Returns the current game step (1, 2, or 3)."""
        return self.step

    def _start_step_2(self) -> None:
        """Starts Step 2 and applies its game rule changes."""
        self._towns.start_step_2()
        self._resource_market.start_step2()
        self._power_plant_market.start_step_2()
        self.step = 2

    def _start_step_3(self) -> None:
        """Starts Step 3 and applies its game rule changes. Also apply any missing Step 2 changes"""
        if self.step == 1:
            self._start_step_2()

        self._towns.start_step_3()
        self._resource_market.start_step3()
        self._power_plant_market.start_step_3()
        self.step = 3

    def check_and_bump_to_step_2(self) -> None:
        """Starts Step 2 at the beginning of Bureaucracy when the city threshold is met.

        The threshold is 7 connected cities for 2-5 players, or 6 for 6 players.
        """
        if self.step != 1:
            return

        if self._towns.get_max_number_of_houses() >= self._step_2_threshold:
            self._start_step_2()

    def check_and_bump_to_step_3(self) -> None:
        """Starts Step 3 at the next phase after the Step 3 card is drawn."""
        if self.step == 3:
            return

        if self._power_plant_market.is_step_3_start():
            self._start_step_3()
