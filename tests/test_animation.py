"""Verificaciones de la traducción de resultados a eventos visuales."""
import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Requiere dependencias de interfaz")
class AnimationTests(unittest.TestCase):
    def test_prim_motion_starts_at_tree_and_keeps_result(self):
        from src.core import Graph
        from src.algorithms.mst import PrimAlgorithm
        from src.ui.animation import graph_playback
        graph = Graph()
        graph.add_edge("A", "B", weight=1)
        graph.add_edge("B", "C", weight=2)
        result = PrimAlgorithm().solve(graph, start="C")
        payload = graph_playback(graph, result, start_node="C")
        visited = {"C"}
        for event in payload["events"]:
            if event["accepted"]:
                arc = event["path"][0]
                edge = payload["edges"][arc["edge"]]
                u, v = edge["source"], edge["target"]
                if arc["reverse"]:
                    u, v = v, u
                self.assertIn(u, visited)
                self.assertNotIn(v, visited)
                visited.add(v)
        self.assertEqual(result.total_weight, 3)

    def test_flow_playback_cancels_original_arc(self):
        from src.core import Graph
        from src.algorithms.flow import FordFulkersonAlgorithm
        from src.ui.animation import graph_playback
        graph = Graph(directed=True)
        for u, v in [("S", "A"), ("S", "B"), ("A", "C"), ("A", "D"),
                     ("B", "C"), ("C", "T"), ("D", "T")]:
            graph.add_edge(u, v, capacity=1)
        result = FordFulkersonAlgorithm().solve(graph, source="S", sink="T")
        payload = graph_playback(graph, result)
        flows = [0] * len(graph.edges)
        inverse = False
        for event in payload["events"]:
            for arc in event["path"]:
                inverse |= arc["reverse"]
                flows[arc["edge"]] += event["amount"] * (-1 if arc["reverse"] else 1)
        self.assertTrue(inverse)
        self.assertEqual(flows, [item.flow for item in result.edge_flows])

    def test_user_labels_cannot_close_payload_script(self):
        import json
        from src.core import Graph
        from src.algorithms.mst import KruskalAlgorithm
        from src.ui.animation import graph_playback, playback_html
        label = '</script><script>alert("x")</script>'
        graph = Graph()
        graph.add_edge(label, "B", weight=1)
        payload = graph_playback(graph, KruskalAlgorithm().solve(graph))
        html = playback_html(payload)
        encoded = html.split('<script id="playback-data" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertNotIn('</script>', encoded)
        self.assertIn(label, json.loads(encoded)["nodes"])
