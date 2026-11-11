import unittest

from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.simple_types import PowerPlant, PowerPlantNumber, Resource


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


if __name__ == "__main__":
    unittest.main()
