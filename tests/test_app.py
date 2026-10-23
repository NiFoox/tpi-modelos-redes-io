"""Comprobaciones de integración opcionales si Streamlit está instalado."""

import importlib.util
import unittest
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Requiere dependencias de interfaz")
class AppTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=30).run()

    def assert_healthy(self, app):
        self.assertEqual(list(app.exception), [])
        self.assertEqual(list(app.error), [])

    def test_six_algorithms_from_editors_to_results(self):
        app = self.app()
        for algorithm, expected in [("Prim", "7"), ("Kruskal", "7"),
                                    ("Dijkstra", "7"), ("Flujo máximo", "17")]:
            with self.subTest(algorithm=algorithm):
                app.selectbox(key="algorithm_Redes").select(algorithm).run()
                app.button(key="solve").click().run()
                self.assert_healthy(app)
                self.assertEqual(app.metric[0].value, expected)
        app.radio(key="area").set_value("Proyectos").run()
        for algorithm in ["CPM", "PERT"]:
            app.selectbox(key="algorithm_Proyectos").select(algorithm).run()
            if algorithm == "PERT":
                app.checkbox(key="use_deadline").check().run()
            app.button(key="solve").click().run()
            self.assert_healthy(app)
            self.assertEqual(app.metric[0].value, "15")
        self.assertEqual(app.metric[-1].value, "71.5%")

    def test_changed_inputs_hide_old_solution_and_large_graph_runs(self):
        app = self.app()
        app.button(key="solve").click().run()
        app.text_area(key="weighted_nodes").set_value("aislado").run()
        self.assertEqual(len(app.metric), 0)
        app.button(key="solve").click().run()
        self.assertTrue(any("desconectado" in e.value for e in app.error))
        app.button(key="generate_weighted").click().run()
        app.button(key="solve").click().run()
        self.assert_healthy(app)
        self.assertEqual(len(app.session_state["solution"][1].nodes), 200)
