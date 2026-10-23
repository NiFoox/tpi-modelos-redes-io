"""Casos esenciales de caminos mínimos."""

import unittest
from math import inf

from src.core import Graph
from src.algorithms.shortest_path import DijkstraAlgorithm


class DijkstraTests(unittest.TestCase):
    def test_relaxation_route_direction_and_isolated_node(self):
        graph = Graph(directed=True)
        for a, b, w in [("A", "B", 9), ("A", "C", 2), ("C", "B", 1),
                        ("B", "D", 2), ("C", "D", 8)]:
            graph.add_edge(a, b, weight=w)
        graph.add_node("E")
        before = graph.edges
        result = DijkstraAlgorithm().solve(graph, source="A", target="D")
        self.assertEqual((result.distance, result.path), (5, ("A", "C", "B", "D")))
        self.assertEqual(dict(result.distances)["E"], inf)
        self.assertTrue(any(s.previous_distance == 9 and s.candidate_distance == 3
                            for s in result.steps))
        self.assertFalse(DijkstraAlgorithm().solve(graph, source="D", target="A").reachable)
        self.assertEqual(graph.edges, before)

    def test_zero_weight_undirected_and_same_endpoint(self):
        graph = Graph()
        graph.add_edge("B", "A", weight=0)
        graph.add_edge("B", "C", weight=2.5)
        result = DijkstraAlgorithm().solve(graph, source="A", target="C")
        self.assertEqual(result.distance, 2.5)
        self.assertEqual(DijkstraAlgorithm().solve(graph, source="A", target="A").path, ("A",))

    def test_invalid_weights_and_nodes(self):
        for kwargs in [{"weight": -1}, {"capacity": 1}]:
            graph = Graph()
            graph.add_edge("A", "B", **kwargs)
            with self.assertRaisesRegex(ValueError, "no negativos"):
                DijkstraAlgorithm().solve(graph, source="A", target="B")
        with self.assertRaisesRegex(ValueError, "No existe"):
            DijkstraAlgorithm().solve(Graph(), source="X", target="Y")
