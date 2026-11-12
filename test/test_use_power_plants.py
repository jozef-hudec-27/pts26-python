from copy import deepcopy
import unittest

from power_grid.simple_types import PowerPlant, PowerPlantNumber, RequestError, Resource
from power_grid.use_power_plants import UsePowerPlants


class TestUsePowerPlants(unittest.TestCase):
    def setUp(self) -> None:
        self.generation = UsePowerPlants()
        self.coal_plant = PowerPlant(PowerPlantNumber(4), 2, 1, [Resource.COAL])
        self.oil_plant = PowerPlant(PowerPlantNumber(3), 2, 1, [Resource.OIL])
        self.hybrid_plant = PowerPlant(
            PowerPlantNumber(5), 2, 1, [Resource.COAL, Resource.OIL]
        )
        self.ecological_plant = PowerPlant(PowerPlantNumber(13), 0, 1)

    def test_empty_selection_supplies_zero_towns_and_accepts_no_fuel(self) -> None:
        self.assertEqual(self.generation.number_of_suppliable_towns([], []), 0)
        for resource in Resource:
            with self.subTest(resource=resource):
                self.assertIsInstance(
                    self.generation.number_of_suppliable_towns([resource], []), RequestError
                )

    def test_single_resource_plant_uses_exact_fuel_requirement(self) -> None:
        for resource in Resource:
            with self.subTest(resource=resource):
                plant = PowerPlant(PowerPlantNumber(10), 2, 3, [resource])
                self.assertEqual(
                    self.generation.number_of_suppliable_towns([resource] * 2, [plant]), 3
                )

    def test_incorrect_fuel_amount_is_rejected(self) -> None:
        for amount in (0, 1, 3, 4):
            with self.subTest(amount=amount):
                self.assertIsInstance(
                    self.generation.number_of_suppliable_towns(
                        [Resource.COAL] * amount, [self.coal_plant]
                    ),
                    RequestError,
                )

    def test_correct_total_with_incompatible_fuel_is_rejected(self) -> None:
        for resources in (
            [Resource.OIL] * 2,
            [Resource.GARBAGE] * 2,
            [Resource.URANIUM] * 2,
            [Resource.COAL, Resource.OIL],
        ):
            with self.subTest(resources=resources):
                self.assertIsInstance(
                    self.generation.number_of_suppliable_towns(resources, [self.coal_plant]),
                    RequestError,
                )

    def test_ecological_plants_need_no_fuel(self) -> None:
        second_ecological_plant = PowerPlant(PowerPlantNumber(18), 0, 2)
        self.assertEqual(
            self.generation.number_of_suppliable_towns([], [self.ecological_plant]), 1
        )
        self.assertEqual(
            self.generation.number_of_suppliable_towns(
                [], [self.ecological_plant, second_ecological_plant]
            ),
            3,
        )
        self.assertIsInstance(
            self.generation.number_of_suppliable_towns(
                [Resource.COAL], [self.ecological_plant]
            ),
            RequestError,
        )

    def test_supplied_towns_are_summed_across_selected_plants(self) -> None:
        garbage_plant = PowerPlant(PowerPlantNumber(6), 1, 1, [Resource.GARBAGE])
        uranium_plant = PowerPlant(PowerPlantNumber(11), 1, 2, [Resource.URANIUM])
        resources = [Resource.COAL] * 2 + [Resource.OIL] * 2
        resources += [Resource.GARBAGE, Resource.URANIUM]
        plants = [
            self.coal_plant, self.oil_plant, garbage_plant, uranium_plant,
            self.ecological_plant,
        ]
        self.assertEqual(self.generation.number_of_suppliable_towns(resources, plants), 6)

    def test_hybrid_accepts_any_valid_fuel_mix(self) -> None:
        for coal_count in range(3):
            with self.subTest(coal_count=coal_count):
                resources = [Resource.COAL] * coal_count + [Resource.OIL] * (2 - coal_count)
                self.assertEqual(
                    self.generation.number_of_suppliable_towns(
                        resources, [self.hybrid_plant]
                    ),
                    1,
                )

    def test_hybrid_allocation_does_not_depend_on_input_order(self) -> None:
        resources = [Resource.COAL] * 2 + [Resource.OIL] * 2
        for plants in (
            [self.hybrid_plant, self.coal_plant],
            [self.coal_plant, self.hybrid_plant],
        ):
            for fuel in (resources, list(reversed(resources))):
                with self.subTest(plants=plants, fuel=fuel):
                    self.assertEqual(
                        self.generation.number_of_suppliable_towns(fuel, plants), 2
                    )

    def test_hybrid_fuel_cannot_cover_an_unfuelled_plant(self) -> None:
        garbage_plant = PowerPlant(PowerPlantNumber(14), 2, 2, [Resource.GARBAGE])
        resources = [Resource.COAL] * 2 + [Resource.OIL] * 2
        self.assertIsInstance(
            self.generation.number_of_suppliable_towns(
                resources, [self.hybrid_plant, garbage_plant]
            ),
            RequestError,
        )

    def test_repeated_plant_numbers_are_rejected(self) -> None:
        duplicate_number = PowerPlant(PowerPlantNumber(4), 2, 2, [Resource.OIL])
        for resources, plants in (
            ([Resource.COAL] * 4, [self.coal_plant, self.coal_plant]),
            ([Resource.COAL] * 2 + [Resource.OIL] * 2,
             [self.coal_plant, duplicate_number]),
            ([], [self.ecological_plant, self.ecological_plant]),
        ):
            with self.subTest(plants=plants):
                self.assertIsInstance(
                    self.generation.number_of_suppliable_towns(resources, plants),
                    RequestError,
                )

    def test_accepts_tuple_inputs(self) -> None:
        resources = (Resource.COAL, Resource.COAL, Resource.OIL, Resource.OIL)
        plants = (self.hybrid_plant, self.coal_plant)
        self.assertEqual(self.generation.number_of_suppliable_towns(resources, plants), 2)

    def test_does_not_mutate_inputs(self) -> None:
        for coal_count in (1, 2):
            with self.subTest(coal_count=coal_count):
                resources = [Resource.COAL] * coal_count + [Resource.OIL] * (4 - coal_count)
                plants = [self.hybrid_plant, self.coal_plant]
                original_resources = list(resources)
                original_plants = deepcopy(plants)
                result = self.generation.number_of_suppliable_towns(resources, plants)
                if coal_count == 2:
                    self.assertEqual(result, 2)
                else:
                    self.assertIsInstance(result, RequestError)
                self.assertEqual(resources, original_resources)
                self.assertEqual(plants, original_plants)


if __name__ == "__main__":
    unittest.main()
