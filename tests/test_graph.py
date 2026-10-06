"""Verifica contratos públicos y consistencia tras operaciones e intentos inválidos."""

import unittest
from dataclasses import FrozenInstanceError

from src.core import Edge, Graph


class EdgeTests(unittest.TestCase):
    def test_weight_and_capacity_have_distinct_meanings(self):
        self.assertIsNone(Edge("A", "B", weight=0).capacity)
        self.assertIsNone(Edge("A", "B", capacity=0).weight)
        self.assertEqual(Edge("A", "B", weight=-3).weight, -3)
        self.assertEqual(Edge("A", "B", weight=2.5, capacity=8).capacity, 8)

    def test_missing_values_loop_and_negative_capacity_are_rejected(self):
        for kwargs in ({}, {"capacity": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Edge("A", "B", **kwargs)
        with self.assertRaises(ValueError):
            Edge("A", "A", weight=1)

    def test_non_finite_values_are_rejected(self):
        for field in ("weight", "capacity"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    Edge("A", "B", **{field: value})

    def test_non_numeric_values_and_booleans_are_rejected(self):
        for field in ("weight", "capacity"):
            for value in (True, False, "3", 2 + 1j):
                with self.subTest(field=field, value=value), self.assertRaises(TypeError):
                    Edge("A", "B", **{field: value})

    def test_invalid_identifiers_are_rejected_at_both_ends(self):
        for invalid in ("", " ", " A", "A ", 1, None):
            for source, target in ((invalid, "B"), ("A", invalid)):
                with self.subTest(source=source, target=target):
                    with self.assertRaises((ValueError, TypeError)):
                        Edge(source, target, weight=1)

    def test_edge_cannot_be_mutated(self):
        edge = Edge("A", "B", weight=1)
        with self.assertRaises(FrozenInstanceError):
            edge.weight = 9


class GraphTests(unittest.TestCase):
    def test_empty_graph_and_isolated_node(self):
        graph = Graph()
        self.assertEqual((graph.nodes, graph.edges), ((), ()))
        graph.add_node("Depósito")
        graph.add_node("Depósito")
        self.assertEqual(graph.nodes, ("Depósito",))
        self.assertEqual(graph.neighbors("Depósito"), ())

    def test_undirected_connection_is_traversable_in_both_directions(self):
        graph = Graph()
        edge = graph.add_edge("A", "B", weight=4)
        self.assertEqual(graph.nodes, ("A", "B"))
        self.assertEqual(graph.edges, (edge,))
        self.assertEqual(graph.neighbors("A"), (("B", edge),))
        self.assertEqual(graph.neighbors("B"), (("A", edge),))

    def test_directed_connections_and_antiparallel_arcs(self):
        graph = Graph(directed=True)
        forward = graph.add_edge("A", "B", capacity=10)
        self.assertEqual(graph.neighbors("B"), ())
        backward = graph.add_edge("B", "A", capacity=3)
        self.assertEqual(graph.neighbors("A"), (("B", forward),))
        self.assertEqual(graph.neighbors("B"), (("A", backward),))
        graph.remove_edge("A", "B")
        self.assertEqual(graph.edges, (backward,))
        self.assertEqual(graph.neighbors("A"), ())
        self.assertEqual(graph.neighbors("B"), (("A", backward),))

    def test_duplicate_edges_are_rejected_without_changing_original(self):
        for directed in (False, True):
            graph = Graph(directed=directed)
            original = graph.add_edge("A", "B", weight=4)
            pairs = [("A", "B")] if directed else [("A", "B"), ("B", "A")]
            for source, target in pairs:
                with self.subTest(directed=directed, source=source):
                    with self.assertRaises(ValueError):
                        graph.add_edge(source, target, weight=99)
                    self.assertEqual(graph.edges, (original,))
                    self.assertEqual(graph.neighbors("A"), (("B", original),))

    def test_failed_insertions_do_not_create_nodes(self):
        graph = Graph()
        graph.add_node("existente")
        for kwargs in ({}, {"capacity": -1}, {"weight": float("nan")}):
            with self.assertRaises(ValueError):
                graph.add_edge("nuevo1", "nuevo2", **kwargs)
            self.assertEqual(graph.nodes, ("existente",))
            self.assertEqual(graph.edges, ())

    def test_public_views_are_immutable_snapshots(self):
        graph = Graph()
        graph.add_edge("A", "B", weight=1)
        nodes, edges, neighbors = graph.nodes, graph.edges, graph.neighbors("A")
        graph.add_edge("A", "C", weight=2)
        self.assertEqual(nodes, ("A", "B"))
        self.assertEqual(len(edges), 1)
        self.assertEqual(len(neighbors), 1)
        with self.assertRaises(AttributeError):
            graph.directed = True

    def test_remove_undirected_edge_in_reverse_preserves_nodes(self):
        graph = Graph()
        graph.add_edge("Z", "A", weight=1)
        graph.remove_edge("A", "Z")
        self.assertEqual(graph.nodes, ("Z", "A"))
        self.assertEqual(graph.edges, ())
        self.assertEqual(graph.neighbors("Z"), ())
        self.assertEqual(graph.neighbors("A"), ())

    def test_remove_node_cleans_all_incident_connections(self):
        for directed in (False, True):
            with self.subTest(directed=directed):
                graph = Graph(directed=directed)
                graph.add_edge("A", "B", weight=1)
                graph.add_edge("B", "C", weight=2)
                keep = graph.add_edge("C", "D", weight=3)
                if directed:
                    graph.add_edge("B", "A", weight=4)
                graph.remove_node("B")
                self.assertEqual(graph.nodes, ("A", "C", "D"))
                self.assertEqual(graph.edges, (keep,))
                self.assertEqual(graph.neighbors("A"), ())
                self.assertEqual(graph.neighbors("C"), (("D", keep),))

    def test_remove_isolated_node(self):
        graph = Graph()
        graph.add_node("A")
        graph.remove_node("A")
        self.assertEqual(graph.nodes, ())

    def test_unknown_nodes_or_connections_report_an_error(self):
        graph = Graph()
        for operation in (lambda: graph.neighbors("A"), lambda: graph.remove_node("A"),
                          lambda: graph.remove_edge("A", "B")):
            with self.assertRaises(ValueError):
                operation()

    def test_direction_and_node_identifiers_are_validated(self):
        with self.assertRaises(TypeError):
            Graph(directed="False")
        graph = Graph()
        for node in ("", " A ", 7):
            with self.assertRaises((TypeError, ValueError)):
                graph.add_node(node)
        self.assertEqual(graph.nodes, ())

    def test_200_nodes_and_disconnected_components(self):
        graph = Graph()
        for i in range(200):
            graph.add_node(str(i))
        for i in range(198):
            graph.add_edge(str(i), str(i + 1), weight=i)
        self.assertEqual(len(graph.nodes), 200)
        self.assertEqual(len(graph.edges), 198)
        self.assertEqual(graph.neighbors("199"), ())
        self.assertEqual(sum(len(graph.neighbors(n)) for n in graph.nodes), 396)


if __name__ == "__main__":
    unittest.main()
