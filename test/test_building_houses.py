from typing import Sequence
import unittest

from power_grid.building_houses import BuildingHouses
from power_grid.interfaces import (
    InterfacePlayerBoardBuildingHouses,
    InterfaceTownsBuildingHouses,
)
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError

class TownsStub(InterfaceTownsBuildingHouses):
    def __init__(self) -> None:
        """Creates configurable responses and records purchase requests."""
        self.result: int | RequestError = 23
        self.max_houses = 0
        self.requests: list[tuple[PlayerColor, tuple[str, ...], int]] = []

    def buy_houses(
        self, player: PlayerColor, town_names: Sequence[str], max_money: int
    ) -> int | RequestError:
        """Records the request and returns the configured result."""
        self.requests.append((player, tuple(town_names), max_money))
        return self.result

    def get_max_number_of_houses(self) -> int:
        """Returns the configured maximum house count."""
        return self.max_houses

class PlayerBoardFake(InterfacePlayerBoardBuildingHouses):
    def __init__(self, money: int = 50) -> None:
        """Creates a small money balance and a payment history."""
        self.money = money
        self.payments: list[int] = []

    def outstanding_money(self) -> int:
        """Returns the current balance."""
        return self.money

    def spend_money(self, amount: int) -> None:
        """Deducts an affordable amount and records the payment."""
        if amount < 0 or amount > self.money:
            raise ValueError("Invalid payment.")
        self.money -= amount
        self.payments.append(amount)

class TestBuildingHouses(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = TownsStub()
        self.red_board = PlayerBoardFake()
        self.blue_board = PlayerBoardFake(40)
        self.boards: dict[PlayerColor, PlayerBoardFake] = {
            PlayerColor.BLUE: self.blue_board,
            PlayerColor.RED: self.red_board,
        }
        self.phase = BuildingHouses(self.towns, self.boards)

    def test_purchase_before_start_is_rejected(self) -> None:
        self.assertIsInstance(
            self.phase.buy_houses(PlayerColor.BLUE, ["A"]), RequestError
        )
        self.assertEqual(self.towns.requests, [])
        self.assertEqual(self.blue_board.payments, [])

    def test_players_act_in_turn_order(self) -> None:
        order = (PlayerColor.RED, PlayerColor.YELLOW, PlayerColor.BLUE)
        boards = {player: PlayerBoardFake() for player in order}
        phase = BuildingHouses(self.towns, boards)
        phase.start_phase(order)
        for player, expected in (
            (PlayerColor.BLUE, PhaseStatus.PHASE_CONTINUES),
            (PlayerColor.YELLOW, PhaseStatus.PHASE_CONTINUES),
            (PlayerColor.RED, PhaseStatus.PHASE_ENDS),
        ):
            self.assertEqual(phase.buy_houses(player, ["A"]), expected)
        self.assertEqual([request[0] for request in self.towns.requests], list(reversed(order)))

    def test_wrong_or_unknown_player_cannot_buy_or_pass(self) -> None:
        self.phase.start_phase((PlayerColor.RED, PlayerColor.BLUE))
        before = self.phase.get_state()
        for player in (PlayerColor.RED, PlayerColor.GREEN):
            for targets in([],["A"]):
                with self.subTest(player=player, targets=targets):
                    self.assertIsInstance(self.phase.buy_houses(player, targets), RequestError)
                    self.assertEqual(self.phase.get_state(), before)
        self.assertEqual(self.towns.requests, [])
        self.assertEqual(self.red_board.payments, [])
        self.assertEqual(self.blue_board.payments, [])

    def test_success_passes_budget_and_deducts_exact_price(self) -> None:
        self.phase.start_phase([PlayerColor.RED,PlayerColor.BLUE])
        self.assertEqual(
            self.phase.buy_houses(PlayerColor.BLUE, ["A", "B"]), PhaseStatus.PHASE_CONTINUES
            )
        self.assertEqual(self.towns.requests, [(PlayerColor.BLUE, ("A", "B"), 40)])
        self.assertEqual(self.blue_board.money, 17)
        self.assertEqual(self.blue_board.payments, [23])
        self.assertEqual(self.red_board.money, 50)

    def test_error_preserves_money_and_allows_retry(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        before = self.phase.get_state()
        error = RequestError("Not enough money.")
        self.towns.result = error
        self.assertIs(self.phase.buy_houses(PlayerColor.BLUE, ["A"]), error)
        self.assertEqual(self.phase.get_state(), before)
        self.assertEqual(self.blue_board.money, 40)
        self.assertEqual(self.blue_board.payments, [])
        self.towns.result = 15
        self.assertEqual(
            self.phase.buy_houses(PlayerColor.BLUE, ["B"]), PhaseStatus.PHASE_CONTINUES
        )
        self.assertEqual(self.blue_board.money, 25)

    def test_empty_request_passes_without_buying_or_spending(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.assertEqual(
            self.phase.buy_houses(PlayerColor.BLUE, []), PhaseStatus.PHASE_CONTINUES
        )
        self.assertEqual(self.phase.buy_houses(PlayerColor.RED, ()), PhaseStatus.PHASE_ENDS)
        self.assertEqual(self.towns.requests, [])
        self.assertEqual(self.red_board.payments, [])
        self.assertEqual(self.blue_board.payments, [])

    def test_succesful_player_cannot_take_another_turn(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.phase.buy_houses(PlayerColor.BLUE, ["A"])
        self.assertIsInstance(self.phase.buy_houses(PlayerColor.BLUE, ["B"]), RequestError)
        self.assertEqual(len(self.towns.requests), 1)
        self.assertEqual(self.blue_board.payments, [23])

    def test_purchase_after_phase_ends_is_rejected(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.phase.buy_houses(PlayerColor.BLUE, [])
        self.phase.buy_houses(PlayerColor.RED, [])
        self.assertIsInstance(self.phase.buy_houses(PlayerColor.RED, ["A"]), RequestError)
        self.assertEqual(self.towns.requests, [])

    def test_game_end_thresholds_and_remaining_players_turn(self) -> None:
        for count, threshold in ((2, 18), (3, 17), (4, 17), (5, 15), (6, 14)):
            for maximum in (threshold - 1, threshold, threshold + 1):
                with self.subTest(count=count, maximum=maximum):
                    order = list(PlayerColor)[:count]
                    towns = TownsStub()
                    boards = {player: PlayerBoardFake() for player in order}
                    phase = BuildingHouses(towns, boards)
                    phase.start_phase(order)
                    towns.max_houses = maximum
                    for player in reversed(order[1:]):
                        self.assertEqual(
                            phase.buy_houses(player, ["A"]), PhaseStatus.PHASE_CONTINUES
                        )
                    expected = (
                        PhaseStatus.GAME_ENDS if maximum >= threshold else PhaseStatus.PHASE_ENDS
                    )
                    self.assertEqual(phase.buy_houses(order[0], ["B"]), expected)

    def test_invalid_player_counts_are_rejected(self) -> None:
        for count in (0,1):
            with self.subTest(count=count):
                boards = {player: PlayerBoardFake() for player in list(PlayerColor)[:count]}
                with self.assertRaises(ValueError):
                    BuildingHouses(self.towns, boards)

    def test_invalid_orders_are_rejected_before_starting(self) -> None:
        orders: tuple[tuple[PlayerColor, ...], ...] = (
            (),(PlayerColor.RED,),(PlayerColor.RED,PlayerColor.RED),
            (PlayerColor.RED,PlayerColor.GREEN),
            (PlayerColor.RED,PlayerColor.BLUE,PlayerColor.GREEN),
        )
        before = self.phase.get_state()
        for order in orders:
            with self.subTest(order=order):
                with self.assertRaises(ValueError):
                    self.phase.start_phase(order)
                self.assertEqual(self.phase.get_state(), before)

    def test_active_phase_cannot_be_restarted(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.phase.buy_houses(PlayerColor.BLUE, [])
        before = self.phase.get_state()
        with self.assertRaises(ValueError):
            self.phase.start_phase([PlayerColor.BLUE, PlayerColor.RED])
        self.assertEqual(self.phase.get_state(), before)
        self.assertEqual(self.phase.buy_houses(PlayerColor.RED, []), PhaseStatus.PHASE_ENDS)

    def test_new_round_can_use_a_new_player_order(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.phase.buy_houses(PlayerColor.BLUE, [])
        self.phase.buy_houses(PlayerColor.RED, [])
        self.phase.start_phase([PlayerColor.BLUE, PlayerColor.RED])
        self.assertEqual(
            self.phase.buy_houses(PlayerColor.RED, ["A"]), PhaseStatus.PHASE_CONTINUES
        )
        self.assertEqual(self.phase.buy_houses(PlayerColor.BLUE, []), PhaseStatus.PHASE_ENDS)

    def test_game_end_rejects_further_requests_and_restarts(self) -> None:
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.towns.max_houses = 18
        self.phase.buy_houses(PlayerColor.BLUE, [])
        self.assertEqual(self.phase.buy_houses(PlayerColor.RED, []), PhaseStatus.GAME_ENDS)
        self.assertEqual(
            self.phase.get_state(),
            "Status: GAME_ENDS\nCurrent player: None\nRemaining players: None",
        )
        self.assertIsInstance(self.phase.buy_houses(PlayerColor.RED, ["A"]), RequestError)
        with self.assertRaises(ValueError):
            self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])

    def test_constructor_and_phase_copy_input_collections(self) -> None:
        order = [PlayerColor.RED, PlayerColor.BLUE]
        self.phase.start_phase(order)
        self.assertEqual(order, [PlayerColor.RED, PlayerColor.BLUE])
        order.clear()
        self.boards.clear()
        targets = ["A", "B"]
        self.assertEqual(
            self.phase.buy_houses(PlayerColor.BLUE, targets), PhaseStatus.PHASE_CONTINUES
        )
        self.assertEqual(targets, ["A", "B"])
        self.assertEqual(self.blue_board.money, 17)

    def test_state_describes_start_turn_changes_and_completion(self) -> None:
        self.assertEqual(
            self.phase.get_state(),
            "Status: NOT_STARTED\nCurrent player: None\nRemaining players: None",
        )
        self.phase.start_phase([PlayerColor.RED, PlayerColor.BLUE])
        self.assertEqual(
            self.phase.get_state(),
            "Status: PHASE_CONTINUES\nCurrent player: BLUE\nRemaining players: BLUE, RED",
        )
        self.phase.buy_houses(PlayerColor.BLUE, [])
        self.assertEqual(
            self.phase.get_state(),
            "Status: PHASE_CONTINUES\nCurrent player: RED\nRemaining players: RED",
        )
        self.phase.buy_houses(PlayerColor.RED, [])
        self.assertEqual(
            self.phase.get_state(),
            "Status: PHASE_ENDS\nCurrent player: None\nRemaining players: None",
        )

if __name__ == "__main__":
    unittest.main()
