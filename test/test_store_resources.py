from copy import deepcopy
import unittest

from power_grid.simple_types import PowerPlant, PowerPlantNumber, Resource
from power_grid.store_resources import StoreResources


class TestStoreResources(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = StoreResources()
        self.coal_plant = PowerPlant(
            PowerPlantNumber(4), 2, 1, [Resource.COAL]
        )
        self.oil_plant = PowerPlant(
            PowerPlantNumber(3), 2, 1, [Resource.OIL]
        )
        self.hybrid_plant = PowerPlant(
            PowerPlantNumber(5), 2, 1, [Resource.COAL, Resource.OIL]
        )
        self.ecological_plant = PowerPlant(PowerPlantNumber(13), 0, 1)

    def test_empty_resources_always_fit(self) -> None:
        self.assertTrue(self.storage.can_store_resources([], []))
        self.assertTrue(self.storage.can_store_resources([], [self.coal_plant]))
        self.assertTrue(self.storage.can_store_resources([], [self.ecological_plant]))

    def test_resources_do_not_fit_without_plants(self) -> None:
        for resource in Resource:
            with self.subTest(resource=resource):
                self.assertFalse(self.storage.can_store_resources([resource], []))

    def test_single_resource_capacity(self) -> None:
        for resource in Resource:
            plant = PowerPlant(PowerPlantNumber(10), 2, 1, [resource])
            for amount, fits in ((1, True), (4, True), (5, False)):
                with self.subTest(resource=resource, amount=amount):
                    self.assertEqual(
                        self.storage.can_store_resources([resource] * amount, [plant]),
                        fits,
                    )

    def test_incompatible_fuel_cannot_use_spare_capacity(self) -> None:
        self.assertFalse(
            self.storage.can_store_resources([Resource.URANIUM], [self.coal_plant])
        )
        self.assertFalse(
            self.storage.can_store_resources(
                [Resource.COAL] * 5, [self.coal_plant, self.oil_plant]
            )
        )

    def test_ecological_plants_cannot_store_resources(self) -> None:
        for resource in Resource:
            with self.subTest(resource=resource):
                self.assertFalse(
                    self.storage.can_store_resources([resource], [self.ecological_plant])
                )

    def test_capacity_combines_across_matching_plants(self) -> None:
        second_coal_plant = PowerPlant(PowerPlantNumber(8), 3, 2, [Resource.COAL])
        plants = [self.coal_plant, second_coal_plant]
        self.assertTrue(self.storage.can_store_resources([Resource.COAL] * 10, plants))
        self.assertFalse(self.storage.can_store_resources([Resource.COAL] * 11, plants))

    def test_hybrid_capacity_is_shared_between_fuels(self) -> None:
        for coal_count in range(5):
            with self.subTest(coal_count=coal_count):
                resources = [Resource.COAL] * coal_count + [Resource.OIL] * (4 - coal_count)
                self.assertTrue(
                    self.storage.can_store_resources(resources, [self.hybrid_plant])
                )
        self.assertFalse(
            self.storage.can_store_resources(
                [Resource.COAL] * 3 + [Resource.OIL] * 2, [self.hybrid_plant]
            )
        )
        self.assertFalse(
            self.storage.can_store_resources([Resource.GARBAGE], [self.hybrid_plant])
        )

    def test_hybrid_allocation_does_not_depend_on_input_order(self) -> None:
        resources = [Resource.COAL] * 4 + [Resource.OIL] * 4
        for plants in (
            [self.hybrid_plant, self.coal_plant],
            [self.coal_plant, self.hybrid_plant],
        ):
            for fuel in (resources, list(reversed(resources))):
                with self.subTest(plants=plants, fuel=fuel):
                    self.assertTrue(self.storage.can_store_resources(fuel, plants))

    def test_shared_hybrid_capacity_cannot_be_counted_twice(self) -> None:
        resources = [Resource.COAL] * 3 + [Resource.OIL] * 3
        garbage_plant = PowerPlant(PowerPlantNumber(6), 1, 1, [Resource.GARBAGE])
        self.assertFalse(
            self.storage.can_store_resources(
                resources, [self.hybrid_plant, garbage_plant]
            )
        )

    def test_accepts_tuples_without_mutating_inputs(self) -> None:
        resources = (Resource.COAL, Resource.OIL)
        plants = (self.hybrid_plant,)
        original_plants = deepcopy(plants)
        self.assertTrue(self.storage.can_store_resources(resources, plants))
        self.assertEqual(plants, original_plants)
        self.assertEqual(resources, (Resource.COAL, Resource.OIL))

    def test_does_not_mutate_inputs(self) -> None:
        for amount, fits in ((3, True), (5, False)):
            with self.subTest(amount=amount):
                resources = [Resource.COAL] * amount
                plants = [self.hybrid_plant]
                original_resources = list(resources)
                original_plants = deepcopy(plants)
                self.assertEqual(self.storage.can_store_resources(resources, plants), fits)
                self.assertEqual(resources, original_resources)
                self.assertEqual(plants, original_plants)


if __name__ == "__main__":
    unittest.main()
