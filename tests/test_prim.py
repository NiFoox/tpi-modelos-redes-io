"""Verificación esencial de Prim y del contrato compartido de MST."""

import unittest

from src.algorithms.mst import KruskalAlgorithm, PrimAlgorithm
from src.core import Graph


class PrimTests(unittest.TestCase):
    def test_known_tree_and_trace_match_kruskal_cost(self):
        graph = Graph()
        for a, b, w in [("B", "A", 1), ("C", "B", 2), ("A", "C", 3),
                        ("D", "C", 4), ("A", "D", 9)]:
            graph.add_edge(a, b, weight=w)
        before = (graph.nodes, graph.edges)
        result = PrimAlgorithm().solve(graph, start="A")
        self.assertEqual(result.total_weight, 7)
        self.assertEqual(result.total_weight, KruskalAlgorithm().solve(graph).total_weight)
        self.assertEqual(len(result.selected_edges), 3)
        self.assertEqual([s.accepted for s in result.steps], [True, True, False, True])
        self.assertEqual([s.accumulated_weight for s in result.steps], [1, 3, 3, 7])
        self.assertEqual([s.components for s in result.steps], [3, 2, 2, 1])
        self.assertEqual((graph.nodes, graph.edges), before)

    def test_ties_negative_zero_and_different_start_nodes(self):
        graph = Graph()
        for a, b, w in [("A", "B", -2.5), ("A", "C", 0), ("B", "C", 0), ("C", "D", 1)]:
            graph.add_edge(a, b, weight=w)
        for start in graph.nodes:
            with self.subTest(start=start):
                self.assertEqual(PrimAlgorithm().solve(graph, start=start).total_weight, -1.5)

    def test_single_node_has_zero_cost(self):
        graph = Graph()
        graph.add_node("A")
        result = PrimAlgorithm().solve(graph)
        self.assertEqual((result.total_weight, result.selected_edges, result.steps), (0, (), ()))

    def test_invalid_inputs(self):
        directed = Graph(directed=True)
        directed.add_edge("A", "B", weight=1)
        missing = Graph()
        missing.add_edge("A", "B", capacity=1)
        disconnected = Graph()
        disconnected.add_edge("A", "B", weight=1)
        disconnected.add_node("C")
        for graph, message in [(Graph(), "al menos"), (directed, "no dirigido"),
                               (missing, "peso"), (disconnected, "desconectado")]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                PrimAlgorithm().solve(graph)
        with self.assertRaisesRegex(ValueError, "inicial"):
            PrimAlgorithm().solve(disconnected, start="Z")
