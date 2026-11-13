from typing import Sequence
from heapq import heappop, heappush


class Connections:
    def __init__(
        self, distances: Sequence[tuple[str, str, int]]
    ) -> None:
        """Creates a map of connections between towns.
        Each tuple contains two town names and their connection cost.
        Copies the provided distances.
        """

        self._distances = list(distances)
        self._neighbours: dict[str, list[tuple[str, int]]] = {}

        for first, second, cost in self._distances:
            if cost < 0:
                raise ValueError("Connection costs must not be negative.")

            self._neighbours.setdefault(first, []).append((second, cost))
            self._neighbours.setdefault(second, []).append((first, cost))

    def calculate_connecting_cost(
        self, from_towns: Sequence[str], to_towns: Sequence[str]
    ) -> int:
        """Returns the minimum cost of connecting the requested towns.

        New towns may be built in any order. The first town is free when the
        network is empty. Repeated and already owned towns add no cost.
        Unknown towns or unreachable targets raise ValueError.
        """

        connected = set(from_towns)
        remaining = set(to_towns) - connected

        if (connected | set(to_towns)) - self._neighbours.keys():
            raise ValueError("Unknown town.")

        if not remaining:
            return 0

        if not connected:
            connected.add(min(remaining))
            remaining -= connected

        total_cost = 0

        while remaining:
            costs = self._shortest_costs(connected)
            reachable = remaining & costs.keys()

            if not reachable:
                raise ValueError("Requested towns cannot be connected.")

            next_town = min(reachable, key=lambda town: (costs[town], town))
            total_cost += costs[next_town]
            connected.add(next_town)
            remaining.remove(next_town)

        return total_cost

    def _shortest_costs(self, from_towns: set[str]) -> dict[str, int]:
        """Finds cheapest routes from any owned town using Dijkstra's algorithm."""

        costs = dict.fromkeys(from_towns, 0)
        pending: list[tuple[int, str]] = []

        for town in from_towns:
            heappush(pending, (0, town))

        while pending:
            cost, town = heappop(pending)

            if cost != costs[town]:
                continue

            for neighbour, connection_cost in self._neighbours[town]:
                new_cost = cost + connection_cost

                if neighbour not in costs or new_cost < costs[neighbour]:
                    costs[neighbour] = new_cost
                    heappush(pending, (new_cost, neighbour))

        return costs
