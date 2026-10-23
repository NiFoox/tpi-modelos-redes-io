"""Punto de entrada de la aplicación: python -m streamlit run app.py."""

from time import perf_counter

import streamlit as st

from src.algorithms.flow import FordFulkersonAlgorithm
from src.algorithms.mst import KruskalAlgorithm, PrimAlgorithm
from src.algorithms.project import CPMAlgorithm, PERTAlgorithm
from src.algorithms.shortest_path import DijkstraAlgorithm
from src.ui.inputs import graph_input, project_input
from src.ui.results import render_graph_result, render_project_result
from src.ui.visualization import network_figure


st.set_page_config(page_title="Modelos de Redes · IO", page_icon="🔗", layout="wide")
st.title("Modelos de Redes")
st.caption("Investigación Operativa · UTN FRVT · Modelá, resolvé y explorá el procedimiento.")

with st.sidebar:
    st.header("Elegí un problema")
    area = st.radio("Área", ["Redes", "Proyectos"], key="area")
    options = ["Prim", "Kruskal", "Dijkstra", "Flujo máximo"] if area == "Redes" else ["CPM", "PERT"]
    algorithm = st.selectbox("Algoritmo", options, key=f"algorithm_{area}")
    descriptions = {"Prim": "Conectar todos los nodos con costo total mínimo, expandiendo un árbol.",
                    "Kruskal": "Conectar todos los nodos eligiendo aristas por peso y evitando ciclos.",
                    "Dijkstra": "Encontrar caminos mínimos con pesos no negativos.",
                    "Flujo máximo": "Transportar la mayor cantidad posible desde una fuente hasta un sumidero.",
                    "CPM": "Planificar actividades con duraciones conocidas y hallar rutas críticas.",
                    "PERT": "Planificar con tres estimaciones de tiempo por actividad."}
    st.info(descriptions[algorithm])
    st.caption("Los ejemplos son editables. También podés cargar un caso nuevo desde cero o importar un CSV.")

try:
    if area == "Redes":
        graph = graph_input(algorithm)
        if not graph.nodes:
            st.info("Agregá nodos o conexiones para comenzar.")
            st.stop()
        st.subheader("2. Resolvé y explorá")
        source, target = None, None
        nodes = list(graph.nodes)
        if algorithm == "Prim":
            source = st.selectbox("Nodo inicial", nodes, key="prim_start")
        elif algorithm in ("Dijkstra", "Flujo máximo"):
            col1, col2 = st.columns(2)
            source = col1.selectbox("Fuente" if algorithm == "Flujo máximo" else "Origen", nodes, key="source")
            target = col2.selectbox("Sumidero" if algorithm == "Flujo máximo" else "Destino", nodes,
                                    index=len(nodes)-1, key="target")
        signature = (algorithm, graph.directed, graph.nodes, graph.edges, source, target)
        if st.button("Resolver", type="primary", key="solve"):
            st.session_state.pop("solution", None)
            start = perf_counter()
            if algorithm == "Prim":
                result = PrimAlgorithm().solve(graph, start=source)
            elif algorithm == "Kruskal":
                result = KruskalAlgorithm().solve(graph)
            elif algorithm == "Dijkstra":
                result = DijkstraAlgorithm().solve(graph, source=source, target=target)
            else:
                result = FordFulkersonAlgorithm().solve(graph, source=source, sink=target)
            st.session_state["solution"] = (signature, result, perf_counter() - start)
            st.session_state.pop("mst_step", None)
        saved = st.session_state.get("solution")
        if saved and saved[0] == signature:
            render_graph_result(graph, saved[1], saved[2])
        else:
            st.info("Ejecutá el algoritmo para obtener una solución con los datos actuales.")
            st.plotly_chart(network_figure(graph), use_container_width=True)
    else:
        pert = algorithm == "PERT"
        project = project_input(pert)
        deadline = None
        if pert and st.checkbox("Evaluar un plazo de terminación", key="use_deadline"):
            deadline = st.number_input("Plazo (misma unidad que las duraciones)", min_value=0.0,
                                       value=16.0, key="deadline")
        st.subheader("2. Planificá el proyecto")
        signature = (algorithm, project, deadline)
        if st.button("Resolver", type="primary", key="solve"):
            st.session_state.pop("solution", None)
            start = perf_counter()
            result = PERTAlgorithm().solve(project, deadline=deadline) if pert else CPMAlgorithm().solve(project)
            st.session_state["solution"] = (signature, result, perf_counter() - start)
        saved = st.session_state.get("solution")
        if saved and saved[0] == signature:
            render_project_result(project, saved[1], saved[2])
        else:
            st.info("Ejecutá el algoritmo para calcular tiempos, holguras y rutas críticas.")
except (ValueError, TypeError) as exc:
    st.error(str(exc))
