from copy import deepcopy
import unittest

from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource


class TestPlayerPowerPlants(unittest.TestCase):
    def setUp(self) -> None:
        self.coal_plant = PowerPlant(PowerPlantNumber(4), 2, 1, [Resource.COAL])
        self.ecological_plant = PowerPlant(PowerPlantNumber(13), 0, 1)

    def test_empty_board_has_no_best_power_plant(self) -> None:
        board = PlayerPowerPlants(power_plant_limit=3)
        self.assertIsNone(board.best_power_plant())

    def test_nonpositive_limit_is_rejected(self) -> None:
        for limit in (-3, -1, 0):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    PlayerPowerPlants(power_plant_limit=limit)

    def test_initial_collection_at_limit_is_accepted(self) -> None:
        board = PlayerPowerPlants(
            power_plant_limit=2, power_plants=[self.coal_plant, self.ecological_plant]
        )
        self.assertEqual(board.best_power_plant(), PowerPlantNumber(13))

    def test_initial_collection_above_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PlayerPowerPlants(
                power_plant_limit=1, power_plants=[self.coal_plant, self.ecological_plant]
            )

    def test_repeated_initial_plant_numbers_are_rejected(self) -> None:
        duplicate_number = PowerPlant(PowerPlantNumber(4), 1, 2, [Resource.OIL])
        for plants in (
            [self.coal_plant, self.coal_plant],
            [self.coal_plant, duplicate_number],
        ):
            with self.subTest(plants=plants):
                with self.assertRaises(ValueError):
                    PlayerPowerPlants(power_plant_limit=3, power_plants=plants)

    def test_best_power_plant_uses_highest_number_regardless_of_order(self) -> None:
        large_output_plant = PowerPlant(PowerPlantNumber(3), 2, 9, [Resource.OIL])
        plants = [self.ecological_plant, large_output_plant, self.coal_plant]
        board = PlayerPowerPlants(power_plant_limit=3, power_plants=plants)
        self.assertEqual(board.best_power_plant(), PowerPlantNumber(13))
        self.assertEqual(
            plants, [self.ecological_plant, large_output_plant, self.coal_plant]
        )

    def test_initial_collection_is_copied(self) -> None:
        plants = [self.coal_plant]
        board = PlayerPowerPlants(power_plant_limit=3, power_plants=plants)
        plants.append(self.ecological_plant)
        self.assertEqual(board.best_power_plant(), PowerPlantNumber(4))
        plants.clear()
        self.assertEqual(board.best_power_plant(), PowerPlantNumber(4))

    def test_accepts_tuple_of_initial_plants(self) -> None:
        board = PlayerPowerPlants(power_plant_limit=1, power_plants=(self.coal_plant,))
        self.assertEqual(board.best_power_plant(), PowerPlantNumber(4))


class TestPlayerPowerPlantCalculations(unittest.TestCase):
    def setUp(self) -> None:
        self.coal_plant = PowerPlant(PowerPlantNumber(4), 2, 1, [Resource.COAL])
        self.hybrid_plant = PowerPlant(
            PowerPlantNumber(12), 2, 2, [Resource.COAL, Resource.OIL]
        )
        self.ecological_plant = PowerPlant(PowerPlantNumber(13), 0, 1)
        self.plants = [self.coal_plant, self.hybrid_plant, self.ecological_plant]
        self.board = PlayerPowerPlants(power_plant_limit=3, power_plants=self.plants)

    def test_empty_board_calculations(self) -> None:
        board = PlayerPowerPlants(power_plant_limit=3)
        self.assertTrue(board.can_store_resources([]))
        self.assertFalse(board.can_store_resources([Resource.COAL]))
        self.assertEqual(board.number_of_connectable_cities(list(Resource)), 0)
        self.assertEqual(board.use_power_plant([], []), 0)
        self.assertIsInstance(board.use_power_plant([], [Resource.COAL]), RequestError)

    def test_storage_checks_full_inventory_against_owned_plants(self) -> None:
        self.assertTrue(
            self.board.can_store_resources([Resource.COAL] * 4 + [Resource.OIL] * 4)
        )
        self.assertFalse(self.board.can_store_resources([Resource.OIL] * 5))
        self.assertFalse(self.board.can_store_resources([Resource.GARBAGE]))

    def test_maximum_capacity_uses_available_fuel_and_allows_leftovers(self) -> None:
        self.assertEqual(
            self.board.number_of_connectable_cities(
                [Resource.COAL] * 2 + [Resource.OIL] * 2 + [Resource.URANIUM]
            ),
            4,
        )
        self.assertEqual(
            self.board.number_of_connectable_cities([Resource.COAL, Resource.OIL]), 3
        )

    def test_use_runs_only_the_selected_owned_plants(self) -> None:
        self.assertEqual(
            self.board.use_power_plant(
                [PowerPlantNumber(12)], [Resource.COAL, Resource.OIL]
            ),
            2,
        )
        self.assertEqual(
            self.board.use_power_plant(
                [PowerPlantNumber(13), PowerPlantNumber(4), PowerPlantNumber(12)],
                [Resource.COAL] * 2 + [Resource.OIL] * 2,
            ),
            4,
        )

    def test_unowned_plant_selection_is_rejected(self) -> None:
        self.assertIsInstance(
            self.board.use_power_plant([PowerPlantNumber(13), PowerPlantNumber(99)], []),
            RequestError,
        )

    def test_repeated_plant_selection_is_rejected(self) -> None:
        for number, resources in ((4, [Resource.COAL] * 4), (13, [])):
            with self.subTest(number=number):
                self.assertIsInstance(
                    self.board.use_power_plant(
                        [PowerPlantNumber(number), PowerPlantNumber(number)], resources
                    ),
                    RequestError,
                )

    def test_invalid_exact_fuel_selection_is_rejected(self) -> None:
        for resources in ([], [Resource.COAL], [Resource.COAL] * 3, [Resource.OIL] * 2):
            with self.subTest(resources=resources):
                self.assertIsInstance(
                    self.board.use_power_plant([PowerPlantNumber(4)], resources), RequestError
                )

    def test_calculations_accept_tuple_inputs(self) -> None:
        resources = (Resource.COAL, Resource.COAL, Resource.OIL, Resource.OIL)
        selected = (PowerPlantNumber(4), PowerPlantNumber(12), PowerPlantNumber(13))
        self.assertTrue(self.board.can_store_resources(resources))
        self.assertEqual(self.board.number_of_connectable_cities(resources), 4)
        self.assertEqual(self.board.use_power_plant(selected, resources), 4)

    def test_calculations_leave_inputs_and_board_unchanged(self) -> None:
        resources = [Resource.COAL] * 2 + [Resource.OIL] * 2
        selected = [PowerPlantNumber(4), PowerPlantNumber(12), PowerPlantNumber(13)]
        original_resources = list(resources)
        original_selected = deepcopy(selected)
        original_plants = deepcopy(self.plants)

        self.assertTrue(self.board.can_store_resources(resources))
        self.assertEqual(self.board.number_of_connectable_cities(resources), 4)
        self.assertEqual(self.board.use_power_plant(selected, resources), 4)
        self.assertIsInstance(
            self.board.use_power_plant([PowerPlantNumber(99)], resources), RequestError
        )

        self.assertEqual(resources, original_resources)
        self.assertEqual(selected, original_selected)
        self.assertEqual(self.plants, original_plants)
        self.assertEqual(self.board.best_power_plant(), PowerPlantNumber(13))
        self.assertEqual(self.board.use_power_plant(selected, resources), 4)


if __name__ == "__main__":
    unittest.main()
