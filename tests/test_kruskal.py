"""Casos esenciales de optimalidad, trazabilidad y validación de Kruskal."""

import unittest

from src.algorithms.mst import KruskalAlgorithm
from src.core import Graph


class KruskalTests(unittest.TestCase):
    def test_minimum_tree_and_cycle_trace_without_mutating_input(self):
        graph = Graph()
        for a, b, weight in [("A", "D", 9), ("A", "C", 3), ("C", "D", 4),
                             ("B", "C", 2), ("A", "B", 1)]:
            graph.add_edge(a, b, weight=weight)
        before = (graph.nodes, graph.edges)
        result = KruskalAlgorithm().solve(graph)
        self.assertEqual(result.total_weight, 7)
        self.assertEqual([(e.source, e.target) for e in result.selected_edges],
                         [("A", "B"), ("B", "C"), ("C", "D")])
        self.assertEqual([s.accepted for s in result.steps], [True, True, False, True])
        self.assertEqual([s.accumulated_weight for s in result.steps], [1, 3, 3, 7])
        self.assertEqual([s.components for s in result.steps], [3, 2, 2, 1])
        self.assertEqual((graph.nodes, graph.edges), before)

    def test_ties_negative_and_zero_weights(self):
        edges = [("A", "B", -2.5), ("A", "C", 0), ("B", "C", 0), ("C", "D", 1)]
        results = []
        for order in (edges, list(reversed(edges))):
            graph = Graph()
            for a, b, weight in order:
                graph.add_edge(a, b, weight=weight)
            results.append(KruskalAlgorithm().solve(graph))
        self.assertEqual(results[0].total_weight, -1.5)
        self.assertEqual(results[0].selected_edges, results[1].selected_edges)

    def test_single_node_has_zero_cost(self):
        graph = Graph()
        graph.add_node("A")
        result = KruskalAlgorithm().solve(graph)
        self.assertEqual((result.total_weight, result.selected_edges, result.steps), (0, (), ()))

    def test_invalid_inputs_report_clear_errors(self):
        directed = Graph(directed=True)
        directed.add_edge("A", "B", weight=1)
        missing_weight = Graph()
        missing_weight.add_edge("A", "B", capacity=3)
        disconnected = Graph()
        disconnected.add_edge("A", "B", weight=1)
        disconnected.add_node("C")
        overflow = Graph()
        overflow.add_edge("A", "B", weight=1e308)
        overflow.add_edge("B", "C", weight=1e308)
        for graph, message in [(Graph(), "al menos un nodo"), (directed, "no dirigido"),
                               (missing_weight, "tener un peso"),
                               (disconnected, "desconectado"), (overflow, "rango numérico")]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                KruskalAlgorithm().solve(graph)
