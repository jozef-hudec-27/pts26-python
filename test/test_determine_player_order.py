import unittest

from power_grid.determine_player_order import DeterminePlayerOrder
from power_grid.interfaces import (
    InterfacePlayerBoardDeterminingPlayerOrder,
    InterfaceTownsDeterminePlayerOrder,
)
from power_grid.simple_types import PlayerColor, PowerPlantNumber


class FakeTowns(InterfaceTownsDeterminePlayerOrder):
    def __init__(self) -> None:
        self.houses: dict[PlayerColor, int] = {}

    def get_number_of_houses(self, player: PlayerColor) -> int:
        return self.houses.get(player, 0)

class FakePlayerBoard(InterfacePlayerBoardDeterminingPlayerOrder):
    def __init__(self, plant: int, capacity: int, money: int) -> None:
        self.plant = plant
        self.capacity = capacity
        self.money = money

    def best_power_plant_number(self) -> PowerPlantNumber:
        return PowerPlantNumber(self.plant)

    def number_of_connectable_cities(self) -> int:
        return self.capacity

    def outstanding_money(self) -> int:
        return self.money

class TestDeterminePlayerOrder(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = FakeTowns()
        self.red = FakePlayerBoard(10, 5, 20)
        self.blue = FakePlayerBoard(20, 4, 30)
        self.boards: dict[
            PlayerColor, InterfacePlayerBoardDeterminingPlayerOrder
        ] = {
            PlayerColor.RED: self.red,
            PlayerColor.BLUE: self.blue,
        }
        self.order = DeterminePlayerOrder(self.towns, self.boards)

    def test_reorder_prioritizes_houses(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 6,
            PlayerColor.BLUE: 5,
        }

        self.assertEqual(
            self.order.reorder(),
            [PlayerColor.RED, PlayerColor.BLUE]
        )

    def test_reorder_breaks_house_tie_with_plant_number(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 5,
            PlayerColor.BLUE: 5,
        }

        self.assertEqual(
            self.order.reorder(),
            [PlayerColor.BLUE, PlayerColor.RED]
        )

    def test_result_prioritized_powerable_cities(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 6,
            PlayerColor.BLUE: 7,
        }
        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.RED, PlayerColor.BLUE]
        )

    def test_result_breaks_supply_tie_with_money(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 4,
            PlayerColor.BLUE: 6,
        }
        self.red.money = 40

        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.RED, PlayerColor.BLUE],
        )

    def test_result_limits_supply_to_owned_houses(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 3,
            PlayerColor.BLUE: 4,
        }

        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.BLUE, PlayerColor.RED],
        )

    def test_no_houses_means_zero_powered_cities(self) -> None:
        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.BLUE, PlayerColor.RED],
        )

    def test_complete_ties_preserve_input_order(self) -> None:
        self.red.plant = self.blue.plant = 0
        self.red.money = self.blue.money = 0
        expected = [PlayerColor.RED, PlayerColor.BLUE]

        self.assertEqual(self.order.reorder(), expected)
        self.assertEqual(self.order.game_result(), expected)

    def test_rankings_use_updated_state(self) -> None:
        self.towns.houses = {
            PlayerColor.RED: 6,
            PlayerColor.BLUE: 5,
        }

        self.assertEqual(
            self.order.reorder(),
            [PlayerColor.RED, PlayerColor.BLUE],
        )
        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.RED, PlayerColor.BLUE],
        )

        self.towns.houses[PlayerColor.BLUE] = 7
        self.blue.capacity = 6

        self.assertEqual(
            self.order.reorder(),
            [PlayerColor.BLUE, PlayerColor.RED],
        )
        self.assertEqual(
            self.order.game_result(),
            [PlayerColor.BLUE, PlayerColor.RED],
        )

    def test_empty_players(self) -> None:
        order = DeterminePlayerOrder(self.towns, {})

        self.assertEqual(order.reorder(), [])
        self.assertEqual(order.game_result(), [])

    def test_one_player(self) -> None:
        order = DeterminePlayerOrder(
            self.towns,
            {PlayerColor.RED: self.red},
        )

        self.assertEqual(order.reorder(), [PlayerColor.RED])
        self.assertEqual(order.game_result(), [PlayerColor.RED])

if __name__ == "__main__":
    unittest.main()
