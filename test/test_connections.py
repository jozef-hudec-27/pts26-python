from itertools import permutations
import unittest

from power_grid.connections import Connections


class TestConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.connections = Connections([
            ("A", "B", 4),
            ("B", "C", 3),
            ("A", "C", 12),
            ("C", "D", 2),
            ("B", "D", 10),
        ])

    def test_no_requested_towns_costs_zero(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], []), 0
        )
        self.assertEqual(
            Connections([]).calculate_connecting_cost([], []), 0
        )

    def test_first_town_has_no_connection_cost(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost([], ["D"]), 0
        )

    def test_direct_connection_works_in_both_directions(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["B"]), 4
        )
        self.assertEqual(
            self.connections.calculate_connecting_cost(["B"], ["A"]), 4
        )

        connections = Connections((("A", "B", 4),))
        self.assertEqual(
            connections.calculate_connecting_cost(("A",), ("B",)), 4
        )

    def test_cheaper_indirect_route_can_bypass_towns(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["C"]), 7
        )
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["D"]), 9
        )

    def test_uses_nearest_owned_town(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A", "D"], ["C"]), 2
        )

    def test_new_houses_can_be_used_for_further_connections(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(
                ["A"], ["B", "C", "D"]
            ),
            9,
        )

    def test_target_order_does_not_change_minimum_cost(self) -> None:
        for towns in permutations(["B", "C", "D"]):
            with self.subTest(towns=towns):
                self.assertEqual(
                    self.connections.calculate_connecting_cost(["A"], towns),
                    9,
                )

    def test_empty_network_can_build_multiple_towns(self) -> None:
        for towns in permutations(["A", "C", "D"]):
            with self.subTest(towns=towns):
                self.assertEqual(
                    self.connections.calculate_connecting_cost([], towns),
                    9,
                )

    def test_bypassed_town_is_not_a_free_connection_source(self) -> None:
        connections = Connections([
            ("A", "X", 5),
            ("X", "B", 1),
            ("X", "C", 1),
        ])

        # A to B costs 6; B to C costs another 2.
        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B", "C"]), 8
        )

    def test_bypassed_town_costs_money_when_built_later(self) -> None:
        connections = Connections([
            ("A", "X", 5),
            ("X", "B", 1),
        ])

        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B"]), 6
        )
        self.assertEqual(
            connections.calculate_connecting_cost(["A", "B"], ["X"]), 1
        )

    def test_repeated_and_owned_towns_add_no_cost(self) -> None:
        self.assertEqual(
            self.connections.calculate_connecting_cost(
                ["A", "A"], ["A", "B", "B"]
            ),
            4,
        )
        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["A"]), 0
        )

    def test_zero_cost_connections_and_cycles(self) -> None:
        connections = Connections([
            ("A", "B", 0),
            ("B", "C", 0),
            ("C", "A", 0),
            ("C", "D", 2),
        ])

        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B", "C"]), 0
        )
        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["D"]), 2
        )

    def test_parallel_connections_use_cheapest_cost(self) -> None:
        connections = Connections([
            ("A", "B", 8),
            ("B", "A", 3),
            ("A", "B", 5),
        ])

        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B"]), 3
        )

    def test_negative_cost_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Connections([("A", "B", -1)])

    def test_unknown_towns_are_rejected(self) -> None:
        cases: tuple[tuple[list[str], list[str]], ...] = (
            (["Missing"], ["A"]),
            (["A"], ["Missing"]),
            ([], ["Missing"]),
            (["Missing"], []),
        )

        for owned, targets in cases:
            with self.subTest(owned=owned, targets=targets):
                with self.assertRaises(ValueError):
                    self.connections.calculate_connecting_cost(owned, targets)

    def test_unreachable_targets_are_rejected(self) -> None:
        connections = Connections([
            ("A", "B", 4),
            ("C", "D", 2),
        ])
        cases: tuple[tuple[list[str], list[str]], ...] = (
            (["A"], ["C"]),
            (["A"], ["B", "C"]),
            ([], ["A", "C"]),
        )

        for owned, targets in cases:
            with self.subTest(owned=owned, targets=targets):
                with self.assertRaises(ValueError):
                    connections.calculate_connecting_cost(owned, targets)

    def test_unused_disconnected_component_is_allowed(self) -> None:
        connections = Connections([
            ("A", "B", 4),
            ("C", "D", 2),
        ])

        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B"]), 4
        )
        self.assertEqual(
            connections.calculate_connecting_cost(["A", "C"], ["B", "D"]), 6
        )

    def test_copies_constructor_input(self) -> None:
        distances = [("A", "B", 4)]
        connections = Connections(distances)

        distances.clear()

        self.assertEqual(
            connections.calculate_connecting_cost(["A"], ["B"]), 4
        )

    def test_calls_do_not_mutate_inputs_or_store_player_state(self) -> None:
        owned = ["A"]
        targets = ["B", "C"]

        self.assertEqual(
            self.connections.calculate_connecting_cost(owned, targets), 7
        )
        self.assertEqual(owned, ["A"])
        self.assertEqual(targets, ["B", "C"])

        self.assertEqual(
            self.connections.calculate_connecting_cost(["A"], ["C"]), 7
        )


if __name__ == "__main__":
    unittest.main()
