from copy import deepcopy
from itertools import permutations
import unittest

from power_grid.maximum_number_of_usable_power_plants import MaximumNumberOfUsablePowerPlants
from power_grid.simple_types import PowerPlant, PowerPlantNumber, Resource


class TestMaximumNumberOfUsablePowerPlants(unittest.TestCase):
    def setUp(self) -> None:
        self.generation = MaximumNumberOfUsablePowerPlants()
        self.coal_plant = PowerPlant(PowerPlantNumber(4), 2, 1, [Resource.COAL])
        self.oil_plant = PowerPlant(PowerPlantNumber(3), 2, 1, [Resource.OIL])
        self.hybrid_plant = PowerPlant(
            PowerPlantNumber(5), 2, 1, [Resource.COAL, Resource.OIL]
        )
        self.ecological_plant = PowerPlant(PowerPlantNumber(13), 0, 1)

    def test_no_plants_supply_zero_towns(self) -> None:
        self.assertEqual(self.generation.number_of_suppliable_towns([], []), 0)
        self.assertEqual(self.generation.number_of_suppliable_towns(list(Resource), []), 0)

    def test_fuelled_plants_cannot_run_without_resources(self) -> None:
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [], [self.coal_plant, self.oil_plant, self.hybrid_plant]
            ),
            0,
        )

    def test_ecological_plants_supply_towns_without_fuel(self) -> None:
        second_ecological_plant = PowerPlant(PowerPlantNumber(18), 0, 2)
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [], [self.coal_plant, self.ecological_plant, second_ecological_plant]
            ),
            3,
        )

    def test_single_plant_runs_at_most_once_and_allows_leftover_fuel(self) -> None:
        for resource in Resource:
            plant = PowerPlant(PowerPlantNumber(10), 2, 3, [resource])
            for amount, towns in ((0, 0), (1, 0), (2, 3), (4, 3)):
                with self.subTest(resource=resource, amount=amount):
                    self.assertEqual(
                        self.generation.number_of_suppliable_towns([resource] * amount, [plant]),
                        towns,
                    )

    def test_all_plants_can_run_with_sufficient_fuel(self) -> None:
        garbage_plant = PowerPlant(PowerPlantNumber(6), 1, 1, [Resource.GARBAGE])
        uranium_plant = PowerPlant(PowerPlantNumber(11), 1, 2, [Resource.URANIUM])
        plants = [
            self.coal_plant, self.oil_plant, garbage_plant, uranium_plant,
            self.ecological_plant,
        ]
        resources = [Resource.COAL] * 4 + [Resource.OIL] * 4
        resources += [Resource.GARBAGE] * 2 + [Resource.URANIUM] * 2
        self.assertEqual(self.generation.number_of_suppliable_towns(resources, plants), 6)

    def test_maximizes_towns_rather_than_number_of_plants(self) -> None:
        large_plant = PowerPlant(PowerPlantNumber(20), 2, 5, [Resource.COAL])
        small_plant = PowerPlant(PowerPlantNumber(8), 1, 2, [Resource.COAL])
        other_small_plant = PowerPlant(PowerPlantNumber(15), 1, 2, [Resource.COAL])
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [Resource.COAL] * 2, [small_plant, other_small_plant, large_plant]
            ),
            5,
        )

    def test_combination_can_supply_more_than_the_largest_plant(self) -> None:
        large_plant = PowerPlant(PowerPlantNumber(20), 3, 5, [Resource.COAL])
        small_plant = PowerPlant(PowerPlantNumber(26), 2, 3, [Resource.COAL])
        other_small_plant = PowerPlant(PowerPlantNumber(31), 1, 3, [Resource.COAL])
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [Resource.COAL] * 3, [large_plant, small_plant, other_small_plant]
            ),
            6,
        )

    def test_incompatible_fuel_is_left_unused(self) -> None:
        plants = [self.coal_plant, self.oil_plant, self.hybrid_plant]
        self.assertEqual(
            self.generation.number_of_suppliable_towns([Resource.URANIUM] * 10, plants), 0
        )
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [Resource.COAL] * 2 + [Resource.URANIUM] * 10, plants
            ),
            1,
        )

    def test_hybrid_accepts_any_valid_fuel_mix(self) -> None:
        fuel_mixes = (
            (Resource.COAL, Resource.COAL),
            (Resource.COAL, Resource.OIL),
            (Resource.OIL, Resource.OIL),
        )
        for fuel_mix in fuel_mixes:
            with self.subTest(fuel_mix=fuel_mix):
                self.assertEqual(
                    self.generation.number_of_suppliable_towns(
                        fuel_mix + (Resource.URANIUM,), [self.hybrid_plant]
                    ),
                    1,
                )

    def test_hybrid_allocation_does_not_depend_on_input_order(self) -> None:
        inventory = [Resource.COAL] * 2 + [Resource.OIL] * 2 + [Resource.URANIUM]
        for plants in permutations(
            [self.hybrid_plant, self.coal_plant, self.ecological_plant]
        ):
            for fuel in (inventory, list(reversed(inventory))):
                with self.subTest(plants=plants, fuel=fuel):
                    self.assertEqual(
                        self.generation.number_of_suppliable_towns(fuel, plants), 3
                    )

    def test_plants_competing_for_fuel_cannot_all_run(self) -> None:
        garbage_plant = PowerPlant(PowerPlantNumber(6), 1, 1, [Resource.GARBAGE])
        resources = [Resource.COAL] * 2 + [Resource.OIL] + [Resource.GARBAGE] * 2
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                resources, [self.coal_plant, self.hybrid_plant, garbage_plant]
            ),
            2,
        )

    def test_repeated_plant_numbers_are_not_counted_twice(self) -> None:
        duplicate_number = PowerPlant(PowerPlantNumber(4), 2, 1, [Resource.COAL])
        for resources, plants in (
            ([Resource.COAL] * 4, [self.coal_plant, self.coal_plant]),
            ([Resource.COAL] * 4, [self.coal_plant, duplicate_number]),
            ([], [self.ecological_plant, self.ecological_plant]),
        ):
            with self.subTest(plants=plants):
                self.assertEqual(
                    self.generation.number_of_suppliable_towns(resources, plants), 1
                )

    def test_accepts_tuple_inputs(self) -> None:
        resources = (Resource.COAL, Resource.COAL, Resource.OIL, Resource.OIL)
        plants = (self.hybrid_plant, self.coal_plant)
        self.assertEqual(self.generation.number_of_suppliable_towns(resources, plants), 2)

    def test_does_not_mutate_inputs(self) -> None:
        plants = [self.hybrid_plant, self.coal_plant, self.ecological_plant]
        for resources, towns in (
            ([Resource.COAL] * 2 + [Resource.OIL] * 2, 3),
            ([Resource.URANIUM], 1),
        ):
            with self.subTest(resources=resources):
                original_resources = list(resources)
                original_plants = deepcopy(plants)
                self.assertEqual(
                    self.generation.number_of_suppliable_towns(resources, plants), towns
                )
                self.assertEqual(resources, original_resources)
                self.assertEqual(plants, original_plants)


if __name__ == "__main__":
    unittest.main()
