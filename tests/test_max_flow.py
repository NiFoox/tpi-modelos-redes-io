"""Flujo conocido, cancelación residual y condiciones de entrada."""

import unittest

from src.core import Graph
from src.algorithms.flow import FordFulkersonAlgorithm


class MaxFlowTests(unittest.TestCase):
    def test_known_flow_cut_and_conservation(self):
        graph = Graph(directed=True)
        for u, v, c in [("S", "A", 16), ("S", "B", 13), ("A", "B", 10),
                        ("B", "A", 4), ("A", "C", 12), ("C", "B", 9),
                        ("B", "D", 14), ("D", "C", 7), ("C", "T", 20), ("D", "T", 4)]:
            graph.add_edge(u, v, capacity=c)
        before = graph.edges
        result = FordFulkersonAlgorithm().solve(graph, source="S", sink="T")
        self.assertEqual(result.total_flow, 23)
        self.assertEqual(result.cut_capacity, result.total_flow)
        balances = dict.fromkeys(graph.nodes, 0)
        for item in result.edge_flows:
            self.assertTrue(0 <= item.flow <= item.edge.capacity)
            balances[item.edge.source] -= item.flow
            balances[item.edge.target] += item.flow
        self.assertEqual(balances, {"S": -23, "A": 0, "B": 0, "C": 0, "D": 0, "T": 23})
        self.assertEqual(graph.edges, before)

    def test_reverse_arc_is_needed(self):
        graph = Graph(directed=True)
        for u, v in [("S", "A"), ("S", "B"), ("A", "C"), ("A", "D"),
                     ("B", "C"), ("C", "T"), ("D", "T")]:
            graph.add_edge(u, v, capacity=1)
        result = FordFulkersonAlgorithm().solve(graph, source="S", sink="T")
        self.assertEqual(result.total_flow, 2)
        self.assertTrue(any("Inverso (cancelación)" in step.directions for step in result.steps))

    def test_zero_disconnected_decimals_and_invalid_inputs(self):
        graph = Graph(directed=True)
        graph.add_edge("S", "T", capacity=0)
        self.assertEqual(FordFulkersonAlgorithm().solve(graph, source="S", sink="T").total_flow, 0)
        graph.remove_edge("S", "T")
        graph.add_edge("S", "T", capacity=0.25)
        self.assertEqual(FordFulkersonAlgorithm().solve(graph, source="S", sink="T").total_flow, 0.25)
        for g, source, sink in [(Graph(), "S", "T"), (graph, "X", "T"), (graph, "S", "S")]:
            with self.assertRaises(ValueError):
                FordFulkersonAlgorithm().solve(g, source=source, sink=sink)
        missing = Graph(directed=True)
        missing.add_edge("S", "T", weight=1)
        with self.assertRaisesRegex(ValueError, "capacidad"):
            FordFulkersonAlgorithm().solve(missing, source="S", sink="T")
