"""Resumen, tablas y procedimiento de cada tipo de solución."""

from math import inf, sqrt

import streamlit as st

from src.algorithms.mst import MSTResult
from src.algorithms.project import PERTResult
from src.algorithms.shortest_path import ShortestPathResult
from src.services.data_io import write_csv
from .visualization import network_figure, project_figure, gantt_figure


def _table(rows, filename, *, download=True):
    if not rows:
        st.caption("No hay pasos para esta solución.")
        return
    st.dataframe(rows, hide_index=True, width="stretch")
    if download:
        st.download_button("Descargar tabla CSV", write_csv(rows, list(rows[0])),
                            filename, "text/csv", key=filename)


def render_graph_result(graph, result, elapsed):
    summary, connections, procedure = st.tabs(["Solución", "Conexiones", "Procedimiento"])
    with summary:
        if isinstance(result, MSTResult):
            st.metric("Costo mínimo", f"{result.total_weight:g}")
            selected = [(e.source, e.target) for e in result.selected_edges]
            if result.steps:
                step = st.slider("Ver construcción del árbol", 0, len(result.steps), len(result.steps), key="mst_step")
                selected = [(s.edge.source, s.edge.target) for s in result.steps[:step] if s.accepted]
                st.caption(f"Paso {step}/{len(result.steps)} · Las conexiones elegidas aparecen en verde.")
            labels = None
        elif isinstance(result, ShortestPathResult):
            if result.reachable:
                st.metric("Distancia mínima", f"{result.distance:g}")
                st.write("Ruta: " + " → ".join(result.path))
            else:
                st.warning("No existe una ruta desde el origen hasta el destino.")
            selected = list(zip(result.path, result.path[1:]))
            labels = None
        else:
            st.metric("Flujo máximo", f"{result.total_flow:g}")
            st.caption(f"Capacidad del corte mínimo: {result.cut_capacity:g}. "
                       "Las etiquetas muestran flujo / capacidad.")
            selected = [(f.edge.source, f.edge.target) for f in result.edge_flows if f.flow > 0]
            labels = {(f.edge.source, f.edge.target): f"{f.flow:g} / {f.edge.capacity:g}" for f in result.edge_flows}
            st.write("Lado de la fuente en el corte: " + ", ".join(result.source_side))
        st.plotly_chart(network_figure(graph, selected=selected, labels=labels), use_container_width=True)
        st.caption(f"{len(graph.nodes)} nodos · {len(graph.edges)} conexiones · "
                   f"Cálculo del algoritmo: {elapsed * 1000:.3f} ms")
    with connections:
        if isinstance(result, MSTResult):
            rows = [{"Origen": e.source, "Destino": e.target, "Peso": e.weight} for e in result.selected_edges]
        elif isinstance(result, ShortestPathResult):
            rows = [{"Nodo": n, "Distancia": "Inalcanzable" if d == inf else str(d)} for n, d in result.distances]
        else:
            cut_pairs = {(e.source, e.target) for e in result.cut_edges}
            rows = [{"Origen": f.edge.source, "Destino": f.edge.target,
                     "Capacidad": f.edge.capacity, "Flujo": f.flow,
                     "Corte mínimo": (f.edge.source, f.edge.target) in cut_pairs} for f in result.edge_flows]
        _table(rows, "solucion_red.csv")
    with procedure:
        if isinstance(result, MSTResult):
            rows = [{"Paso": s.iteration, "Origen": s.edge.source, "Destino": s.edge.target,
                     "Peso": s.edge.weight, "Aceptada": s.accepted, "Motivo": s.reason,
                     "Acumulado": s.accumulated_weight} for s in result.steps]
        elif isinstance(result, ShortestPathResult):
            rows = [{"Paso": s.iteration, "Desde": s.source, "Hacia": s.target,
                     "Anterior": "∞" if s.previous_distance == inf else str(s.previous_distance),
                     "Candidata": s.candidate_distance, "Actualizada": s.accepted} for s in result.steps]
        else:
            rows = [{"Paso": s.iteration, "Camino residual": " → ".join(s.path),
                     "Sentidos": "; ".join(s.directions), "Aumento": s.augmentation,
                     "Flujo acumulado": s.total_flow} for s in result.steps]
        _table(rows, "procedimiento_red.csv")


def render_project_result(project, result, elapsed):
    pert = isinstance(result, PERTResult)
    schedule = result.schedule if pert else result
    cols = st.columns(3)
    cols[0].metric("Duración esperada" if pert else "Duración del proyecto", f"{schedule.duration:g}")
    cols[1].metric("Actividades críticas", str(len(schedule.critical_activities)))
    cols[2].metric("Rutas críticas", str(schedule.critical_path_count))
    st.write(("Ruta crítica representativa: " if schedule.critical_path_count > 1 else "Ruta crítica: ") +
             " → ".join(schedule.critical_path))
    if pert:
        st.caption(f"Varianza de la ruta mostrada: {result.critical_path_variance:.6g} · "
                   f"Desviación estándar: {sqrt(result.critical_path_variance):.6g}")
        if result.completion_probability is not None:
            st.metric(f"Probabilidad aproximada de terminar en {result.deadline:g} o antes",
                       f"{result.completion_probability:.1%}")
        if schedule.critical_path_count > 1:
            st.info("Hay varias rutas críticas. No se calcula una probabilidad global a partir de una sola ruta.")
        st.caption("PERT usa la aproximación normal sobre una ruta crítica y supone duraciones independientes. "
                   "La ruta crítica puede cambiar por la variabilidad de los tiempos.")
    network, timings, gantt, steps = st.tabs(["Red del proyecto", "Tiempos y holguras", "Gantt", "Procedimiento"])
    with network:
        st.plotly_chart(project_figure(project, schedule), use_container_width=True)
        st.caption("Actividades en nodos; flechas de precedencia. Las conexiones críticas aparecen en verde.")
    with timings:
        variances = dict(result.variances) if pert else {}
        rows = []
        for t in schedule.timings:
            row = {"Actividad": t.id, "Duración": t.duration, "IC": t.early_start,
                   "TC": t.early_finish, "IL": t.late_start, "TL": t.late_finish,
                   "Holgura": t.slack, "Crítica": t.critical}
            if pert:
                row["Varianza"] = variances[t.id]
            rows.append(row)
        _table(rows, "tiempos_proyecto.csv")
        st.caption("IC/TC: inicio y terminación cercanos. IL/TL: inicio y terminación lejanos.")
    with gantt:
        st.plotly_chart(gantt_figure(schedule), use_container_width=True)
    with steps:
        _table([{"Recorrido": s.phase, "Actividad": s.activity,
                 "Inicio": s.start, "Terminación": s.finish} for s in schedule.steps], "procedimiento_proyecto.csv")
    st.caption(f"Cálculo del algoritmo: {elapsed * 1000:.3f} ms. Todas las duraciones usan la misma unidad.")
