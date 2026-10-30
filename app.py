"""Punto de entrada: python -m streamlit run app.py."""
from time import perf_counter

import streamlit as st

from src.algorithms.flow import FordFulkersonAlgorithm
from src.algorithms.mst import KruskalAlgorithm, PrimAlgorithm
from src.algorithms.project import CPMAlgorithm, PERTAlgorithm
from src.algorithms.shortest_path import DijkstraAlgorithm
from src.ui.inputs import graph_input, project_input
from src.ui.results import render_graph_result, render_project_result
from src.ui.theme import apply_theme, brand, chart, hero, legend, note, section
from src.ui.visualization import network_figure, project_preview

st.set_page_config(page_title="Modelos de Redes · IO", page_icon=":material/hub:", layout="wide")
apply_theme()
with st.sidebar:
    brand()
    area = st.radio("Área de trabajo", ["Redes", "Proyectos"], key="area")
    options = ["Prim", "Kruskal", "Dijkstra", "Flujo máximo"] if area == "Redes" else ["CPM", "PERT"]
    algorithm = st.selectbox("Algoritmo", options, key=f"algorithm_{area}")
    st.divider()
    st.caption("TU RECORRIDO")
    st.markdown("**01** Configurá el problema\n\n**02** Ejecutá y visualizá\n\n**03** Explorá la solución")
    with st.expander("Guía rápida", icon=":material/help_outline:"):
        st.write("Editá las tablas o importá un CSV. Resolvé el problema y explorá las pestañas de resultados. Al cambiar los datos, volvé a resolver para actualizar la solución.")
        st.caption("Los ejemplos son editables. Todas las duraciones de un proyecto deben usar la misma unidad.")
    st.divider()
    st.caption("INVESTIGACIÓN OPERATIVA\n\nUTN · Facultad Regional Venado Tuerto")
hero(algorithm, area)
configuration, workspace = st.columns([.37, .63], gap="large")
try:
    with configuration, st.container(key="configuration"):
        if area == "Redes":
            graph = graph_input(algorithm)
            source, target = None, None
            nodes = list(graph.nodes)
            if nodes:
                if algorithm == "Prim":
                    source = st.selectbox("Nodo inicial", nodes, key="prim_start")
                elif algorithm in ("Dijkstra", "Flujo máximo"):
                    col1, col2 = st.columns(2)
                    source = col1.selectbox("Fuente" if algorithm == "Flujo máximo" else "Origen", nodes, key="source")
                    target = col2.selectbox("Sumidero" if algorithm == "Flujo máximo" else "Destino", nodes,
                                            index=len(nodes)-1, key="target")
            signature = (algorithm, graph.directed, graph.nodes, graph.edges, source, target)
        else:
            pert = algorithm == "PERT"
            project = project_input(pert)
            deadline = None
            if pert and st.checkbox("Evaluar un plazo de terminación", key="use_deadline"):
                deadline = st.number_input("Plazo (misma unidad que las duraciones)", min_value=0.0,
                                           value=16.0, key="deadline")
            signature = (algorithm, project, deadline)
        solve = st.button("Resolver", type="primary", key="solve", icon=":material/play_arrow:",
                          use_container_width=True, disabled=area == "Redes" and not nodes)
        st.caption("Los resultados corresponden a los datos de la última ejecución.")
    with workspace, st.container(key="workspace"):
        section("02", "Visualización y resultados")
        if solve:
            st.session_state.pop("solution", None)
            for key in list(st.session_state):
                if key.startswith("explore_"):
                    del st.session_state[key]
            with st.spinner("Calculando la solución…"):
                start = perf_counter()
                if area == "Proyectos":
                    result = PERTAlgorithm().solve(project, deadline=deadline) if pert else CPMAlgorithm().solve(project)
                elif algorithm == "Prim":
                    result = PrimAlgorithm().solve(graph, start=source)
                elif algorithm == "Kruskal":
                    result = KruskalAlgorithm().solve(graph)
                elif algorithm == "Dijkstra":
                    result = DijkstraAlgorithm().solve(graph, source=source, target=target)
                else:
                    result = FordFulkersonAlgorithm().solve(graph, source=source, sink=target)
                st.session_state["solution"] = (signature, result, perf_counter() - start)
        saved = st.session_state.get("solution")
        if saved and saved[0] == signature:
            if area == "Redes":
                render_graph_result(graph, saved[1], saved[2])
            else:
                render_project_result(project, saved[1], saved[2])
        else:
            note("Tu problema, listo para explorar", "Revisá los datos y pulsá Resolver para calcular la solución. Podés empezar con el ejemplo cargado.")
            if area == "Redes":
                if graph.nodes:
                    chart(network_figure(graph), "network_preview")
                    legend()
                    st.caption(f"{len(graph.nodes)} nodos · {len(graph.edges)} conexiones · {'Dirigida' if graph.directed else 'No dirigida'}")
                else:
                    st.info("Agregá nodos o conexiones para comenzar.")
            else:
                chart(project_preview(project), "project_preview")
                st.caption(f"{len(project.activities)} actividades · Flechas de precedencia")
except (ValueError, TypeError) as exc:
    with workspace:
        st.error(str(exc), icon=":material/error_outline:")
        st.caption("Revisá los datos de configuración y volvé a resolver.")
