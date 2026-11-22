import unittest

from power_grid.check_and_bump_step import CheckAndBumpStep
from power_grid.interfaces import (
    InterfacePowerPlantMarketCheckAndBumpStep,
    InterfaceTownsCheckAndBumpStep,
)
from power_grid.resource_market import ResourceMarket

class FakeTowns(InterfaceTownsCheckAndBumpStep):
    """Provide a house count and record town step changes."""
    def __init__(self) -> None:
        self.max_houses: int = 0
        self.started_steps: list[int] = []

    def get_max_number_of_houses(self) -> int:
        return self.max_houses

    def start_step_2(self) -> None:
        self.started_steps.append(2)

    def start_step_3(self) -> None:
        self.started_steps.append(3)

class FakePowerPlantMarket(InterfacePowerPlantMarketCheckAndBumpStep):

    def __init__(self) -> None:
        self.step_3_drawn: bool = False
        self.started_steps: list[int] = []

    def is_step_3_start(self) -> bool:
        return self.step_3_drawn

    def start_step_2(self) -> None:
        self.started_steps.append(2)

    def start_step_3(self) -> None:
        self.started_steps.append(3)

class FakeResourceMarket(ResourceMarket):

    def __init__(self) -> None: # pylint: disable=super-init-not-called
        # Only the overridden step methods are used in these tests.
        self.started_steps: list[int] = []

    def start_step2(self) -> None:
        self.started_steps.append(2)

    def start_step3(self) -> None:
        self.started_steps.append(3)

class TestCheckAndBumpStep(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = FakeTowns()
        self.power_plant_market = FakePowerPlantMarket()
        self.resource_market = FakeResourceMarket()
        self.steps = self._create_steps(4)

    def _create_steps(self, number_of_players: int) -> CheckAndBumpStep:
        """Create a step tracker using test doubles"""
        return CheckAndBumpStep(
            number_of_players,
            self.towns,
            self.power_plant_market,
            self.resource_market,
        )

    def test_starts_in_step_1(self) -> None:
        self.assertEqual(self.steps.get_step(), 1)
        self.assertEqual(self.towns.started_steps, [])
        self.assertEqual(self.power_plant_market.started_steps, [])
        self.assertEqual(self.resource_market.started_steps, [])

    def test_invalid_number_of_players(self) -> None:
        for number_of_players in (-1, 0, 1, 7):
            with self.subTest(number_of_players=number_of_players):
                with self.assertRaises(ValueError):
                    self._create_steps(number_of_players)

    def test_step_2_thresholds(self) -> None:
        thresholds = {2: 7, 3: 7, 4: 7, 5: 7, 6: 6}

        for number_of_players, threshold in thresholds.items():
            for houses in (threshold - 1, threshold, threshold + 1):
                with self.subTest(
                    number_of_players=number_of_players,
                    houses=houses,
                ):
                    towns = FakeTowns()
                    market = FakePowerPlantMarket()
                    resources = FakeResourceMarket()
                    towns.max_houses = houses

                    steps = CheckAndBumpStep(
                        number_of_players, towns, market, resources
                    )

                    steps.check_and_bump_to_step_2()

                    expected_step = 2 if houses >= threshold else 1
                    expected_changes = [2] if houses >= threshold else []

                    self.assertEqual(steps.get_step(), expected_step)
                    self.assertEqual(towns.started_steps, expected_changes)
                    self.assertEqual(market.started_steps, expected_changes)
                    self.assertEqual(resources.started_steps, expected_changes)

    def test_step_2_starts_after_house_count_increases(self) -> None:
        self.towns.max_houses = 6

        self.steps.check_and_bump_to_step_2()

        self.assertEqual(self.steps.get_step(), 1)
        self.assertEqual(self.towns.started_steps, [])
        self.assertEqual(self.power_plant_market.started_steps, [])
        self.assertEqual(self.resource_market.started_steps, [])

        self.towns.max_houses = 7

        self.steps.check_and_bump_to_step_2()

        self.assertEqual(self.steps.get_step(), 2)
        self.assertEqual(self.towns.started_steps, [2])
        self.assertEqual(self.power_plant_market.started_steps, [2])
        self.assertEqual(self.resource_market.started_steps, [2])

    def test_step_2_changes_are_applied_only_once(self) -> None:
        self.towns.max_houses = 7

        self.steps.check_and_bump_to_step_2()
        self.steps.check_and_bump_to_step_2()

        self.assertEqual(self.steps.get_step(), 2)
        self.assertEqual(self.towns.started_steps, [2])
        self.assertEqual(self.power_plant_market.started_steps, [2])
        self.assertEqual(self.resource_market.started_steps, [2])

    def test_step_3_does_not_start_without_card_in_step_1(self) -> None:
        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 1)
        self.assertEqual(self.towns.started_steps, [])
        self.assertEqual(self.power_plant_market.started_steps, [])
        self.assertEqual(self.resource_market.started_steps, [])

    def test_step_3_does_not_start_without_card_in_step_2(self) -> None:
        self.towns.max_houses = 7
        self.steps.check_and_bump_to_step_2()

        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 2)
        self.assertEqual(self.towns.started_steps, [2])
        self.assertEqual(self.power_plant_market.started_steps, [2])
        self.assertEqual(self.resource_market.started_steps, [2])

    def test_step_3_starts_from_step_2(self) -> None:
        self.towns.max_houses = 7
        self.steps.check_and_bump_to_step_2()
        self.power_plant_market.step_3_drawn = True

        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 3)
        self.assertEqual(self.towns.started_steps, [2, 3])
        self.assertEqual(self.power_plant_market.started_steps, [2, 3])
        self.assertEqual(self.resource_market.started_steps, [2, 3])

    def test_step_3_starts_from_step_1(self) -> None:
        self.power_plant_market.step_3_drawn = True

        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 3)
        self.assertEqual(self.towns.started_steps, [2, 3])
        self.assertEqual(self.power_plant_market.started_steps, [2, 3])
        self.assertEqual(self.resource_market.started_steps, [2, 3])

    def test_step_3_starts_after_card_is_drawn(self) -> None:
        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 1)

        self.power_plant_market.step_3_drawn = True

        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 3)
        self.assertEqual(self.towns.started_steps, [2, 3])
        self.assertEqual(self.power_plant_market.started_steps, [2, 3])
        self.assertEqual(self.resource_market.started_steps, [2, 3])

    def test_checks_do_not_change_step_3(self) -> None:
        self.power_plant_market.step_3_drawn = True
        self.steps.check_and_bump_to_step_3()
        self.towns.max_houses = 20

        self.steps.check_and_bump_to_step_2()
        self.steps.check_and_bump_to_step_3()

        self.assertEqual(self.steps.get_step(), 3)
        self.assertEqual(self.towns.started_steps, [2, 3])
        self.assertEqual(self.power_plant_market.started_steps, [2, 3])
        self.assertEqual(self.resource_market.started_steps, [2, 3])

if __name__ == "__main__":
    unittest.main()
