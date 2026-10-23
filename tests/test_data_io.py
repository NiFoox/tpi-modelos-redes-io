"""Contratos de archivos y validación sin estado parcial."""

import unittest

from src.core import Graph
from src.services.data_io import graph_csv, graph_from_rows, read_csv, project_csv, project_from_rows


class DataIOTests(unittest.TestCase):
    def test_graph_csv_roundtrip_preserves_isolated_and_opposite_edges(self):
        graph = Graph(directed=True)
        graph.add_node("aislado")
        graph.add_edge("A", "B", weight=0, capacity=2.5)
        graph.add_edge("B", "A", capacity=1)
        rows = read_csv(graph_csv(graph).encode("utf-8-sig"),
                        {"origen", "destino"}, {"tipo", "peso", "capacidad"})
        result = graph_from_rows(rows, directed=True)
        self.assertEqual((result.nodes, result.edges), (graph.nodes, graph.edges))

    def test_project_roundtrip_and_malformed_rows(self):
        rows = [{"actividad": "A", "predecesoras": "", "duracion": "2"},
                {"actividad": "B", "predecesoras": "A", "duracion": "3"}]
        project = project_from_rows(rows, pert=False)
        self.assertEqual(project_from_rows(read_csv(project_csv(project, pert=False),
                         {"actividad", "predecesoras", "duracion"}), pert=False), project)
        for text in ["origen,destino\nA,B,3", "origen,origen\nA,B", "origen,destino\nA"]:
            with self.assertRaises(ValueError):
                read_csv(text, {"origen", "destino"})
        with self.assertRaisesRegex(ValueError, "Fila 1"):
            graph_from_rows([{"origen": "A", "destino": "B", "peso": "nan"}], directed=False)
