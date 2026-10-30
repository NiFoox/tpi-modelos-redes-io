"""Métricas, estados del procedimiento y exportación de resultados."""
from math import inf, sqrt

import streamlit as st

from src.algorithms.mst import MSTResult
from src.algorithms.project import PERTResult
from src.algorithms.shortest_path import ShortestPathResult
from src.services.data_io import write_csv
from .theme import chart, legend, metrics, note, section, step_controls
from .visualization import network_figure, project_figure, gantt_figure


def _table(rows, filename, *, download=True):
    if not rows:
        st.caption("No hay pasos para esta solución.")
        return
    st.dataframe(rows, hide_index=True, width="stretch")
    if download:
        st.download_button("Descargar tabla CSV", write_csv(rows, list(rows[0])),
                           filename, "text/csv", key=filename, icon=":material/download:")


def _graph_steps(result):
    if isinstance(result, MSTResult):
        return [{"Paso": s.iteration, "Origen": s.edge.source, "Destino": s.edge.target,
                 "Peso": s.edge.weight, "Aceptada": s.accepted, "Motivo": s.reason,
                 "Acumulado": s.accumulated_weight} for s in result.steps]
    if isinstance(result, ShortestPathResult):
        return [{"Paso": s.iteration, "Desde": s.source, "Hacia": s.target,
                 "Anterior": "∞" if s.previous_distance == inf else str(s.previous_distance),
                 "Candidata": s.candidate_distance, "Actualizada": s.accepted} for s in result.steps]
    return [{"Paso": s.iteration, "Camino residual": " → ".join(s.path),
             "Sentidos": "; ".join(s.directions), "Aumento": s.augmentation,
             "Flujo acumulado": s.total_flow} for s in result.steps]


def _explore_graph(graph, result):
    section("03", "Explorá el procedimiento", "Cada posición corresponde a un paso registrado durante el cálculo.")
    count = step_controls(len(result.steps), "explore_graph_step")
    step = result.steps[count - 1] if count else None
    selected, focus, labels, roles = [], [], None, {}
    if isinstance(result, MSTResult):
        selected = [(s.edge.source, s.edge.target) for s in result.steps[:count] if s.accepted]
        if step:
            focus = [(step.edge.source, step.edge.target)]
            note("Conexión aceptada" if step.accepted else "Conexión descartada",
                 f"{step.edge.source} — {step.edge.target} · Peso {step.edge.weight:g}. {step.reason}. "
                 f"Costo acumulado: {step.accumulated_weight:g}.", tone="success" if step.accepted else "warning")
        else:
            note("Estado inicial", "Todavía no se ha evaluado ninguna conexión.")
    elif isinstance(result, ShortestPathResult):
        distances, parents = {n: inf for n in graph.nodes}, {}
        distances[result.source] = 0
        for s in result.steps[:count]:
            if s.accepted:
                distances[s.target] = s.candidate_distance
                parents[s.target] = s.source
        selected = [(p, n) for n, p in parents.items()]
        roles = {result.source: "Origen", result.target: "Destino"}
        if step:
            focus = [(step.source, step.target)]
            previous = "∞" if step.previous_distance == inf else f"{step.previous_distance:g}"
            note("Distancia actualizada" if step.accepted else "Se conserva la distancia",
                 f"{step.source} → {step.target} · Anterior: {previous} · Candidata: {step.candidate_distance:g}.",
                 tone="success" if step.accepted else "warning")
        else:
            note("Estado inicial", f"Distancia a {result.source}: 0. Los demás nodos comienzan con distancia infinita.")
        st.caption("El grafo muestra las conexiones predecesoras actuales; la ruta definitiva está en Solución.")
        with st.expander("Distancias en este paso"):
            st.dataframe([{"Nodo": n, "Distancia provisional": "∞" if d == inf else f"{d:g}"} for n, d in distances.items()],
                         hide_index=True, width="stretch")
    else:
        flows = {(e.source, e.target): 0 for e in graph.edges}
        for s in result.steps[:count]:
            for (u, v), direction in zip(zip(s.path, s.path[1:]), s.directions):
                if direction == "Directo":
                    flows[u, v] += s.augmentation
                else:
                    flows[v, u] -= s.augmentation
        selected = [pair for pair, flow in flows.items() if flow > 0]
        labels = {(e.source, e.target): f"{flows[e.source, e.target]:g} / {e.capacity:g}" for e in graph.edges}
        roles = {result.source: "Origen", result.sink: "Destino"}
        if step:
            note("Camino aumentante", f"{' → '.join(step.path)} · Aumento: {step.augmentation:g} · "
                 f"Flujo acumulado: {step.total_flow:g}.", tone="success")
            st.caption("Sentidos: " + " · ".join(step.directions))
        else:
            note("Estado inicial", "Flujo cero en todas las conexiones. Las etiquetas muestran flujo / capacidad.")
    chart(network_figure(graph, selected=selected, labels=labels, focus=focus, roles=roles), "graph_steps")
    legend()
    if focus:
        st.caption("Trazo ámbar punteado: conexión evaluada en el paso actual.")
    with st.expander("Registro completo y descarga"):
        _table(_graph_steps(result), "procedimiento_red.csv")


def render_graph_result(graph, result, elapsed):
    if isinstance(result, MSTResult):
        metrics([("Costo mínimo", f"{result.total_weight:g}"), ("Conexiones del árbol", str(len(result.selected_edges))),
                 ("Tiempo de cálculo", f"{elapsed * 1000:.3f} ms")])
    elif isinstance(result, ShortestPathResult):
        metrics([("Distancia mínima", f"{result.distance:g}" if result.reachable else "∞"),
                 ("Nodos en la ruta", str(len(result.path))), ("Tiempo de cálculo", f"{elapsed * 1000:.3f} ms")])
    else:
        metrics([("Flujo máximo", f"{result.total_flow:g}"), ("Corte mínimo", f"{result.cut_capacity:g}"),
                 ("Tiempo de cálculo", f"{elapsed * 1000:.3f} ms")])
    summary, connections, procedure = st.tabs(["Solución", "Conexiones", "Procedimiento"])
    with summary:
        roles = {}
        if isinstance(result, MSTResult):
            selected = [(e.source, e.target) for e in result.selected_edges]
            labels = None
            note("Árbol de expansión mínima", f"{len(result.nodes)} nodos conectados · "
                 f"{len(result.selected_edges)} aristas · Sin ciclos.", tone="success")
        elif isinstance(result, ShortestPathResult):
            if result.reachable:
                note("Ruta más corta", " → ".join(result.path), tone="success")
            else:
                st.warning("No existe una ruta desde el origen hasta el destino.")
            selected = list(zip(result.path, result.path[1:]))
            labels = None
            roles = {result.source: "Origen", result.target: "Destino"}
        else:
            selected = [(f.edge.source, f.edge.target) for f in result.edge_flows if f.flow > 0]
            labels = {(f.edge.source, f.edge.target): f"{f.flow:g} / {f.edge.capacity:g}" for f in result.edge_flows}
            roles = {result.source: "Origen", result.sink: "Destino"}
            note("Capacidad máxima alcanzada", f"Flujo máximo = capacidad del corte mínimo = {result.total_flow:g}. "
                 "Las etiquetas muestran flujo / capacidad.", tone="success")
        chart(network_figure(graph, selected=selected, labels=labels, roles=roles), "graph_solution")
        legend()
        st.caption(f"{len(graph.nodes)} nodos · {len(graph.edges)} conexiones")
        if roles:
            st.caption("Rombo: origen / fuente · Cuadrado: destino / sumidero")
        if not isinstance(result, (MSTResult, ShortestPathResult)):
            with st.expander("Explorar el corte mínimo"):
                st.write("Lado de la fuente: " + ", ".join(result.source_side))
                cut_pairs = [(e.source, e.target) for e in result.cut_edges]
                chart(network_figure(graph, selected=cut_pairs, selected_nodes=result.source_side, labels=labels), "minimum_cut")
                st.caption("Se resaltan las conexiones del corte y los nodos de sus extremos.")
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
        _explore_graph(graph, result)


def render_project_result(project, result, elapsed):
    pert = isinstance(result, PERTResult)
    schedule = result.schedule if pert else result
    metrics([("Duración esperada" if pert else "Duración del proyecto", f"{schedule.duration:g}"),
             ("Actividades críticas", str(len(schedule.critical_activities))),
             ("Rutas críticas", str(schedule.critical_path_count))])
    note("Ruta crítica representativa" if schedule.critical_path_count > 1 else "Ruta crítica",
         " → ".join(schedule.critical_path), tone="success")
    st.caption(f"Tiempo de cálculo: {elapsed * 1000:.3f} ms · Todas las duraciones usan la misma unidad.")
    if pert:
        st.caption(f"Varianza de la ruta mostrada: {result.critical_path_variance:.6g} · "
                   f"Desviación estándar: {sqrt(result.critical_path_variance):.6g}")
        if result.completion_probability is not None:
            with st.container(border=True):
                st.metric(f"Probabilidad aproximada de terminar en {result.deadline:g} o antes",
                          f"{result.completion_probability:.1%}")
                st.progress(result.completion_probability)
        if schedule.critical_path_count > 1:
            st.info("Hay varias rutas críticas. No se calcula una probabilidad global a partir de una sola ruta.")
        with st.expander("Cómo interpretar la estimación PERT", expanded=True):
            st.caption("PERT usa la aproximación normal sobre una ruta crítica y supone duraciones independientes. "
                       "La ruta crítica puede cambiar por la variabilidad de los tiempos. La probabilidad es una aproximación, no una garantía.")
    network, timings, gantt, steps = st.tabs(["Red del proyecto", "Tiempos y holguras", "Gantt", "Procedimiento"])
    with network:
        chart(project_figure(project, schedule), "project_solution")
        legend(project=True)
        st.caption("★ y rombo: actividad crítica. Su holgura es cero; una demora retrasa el proyecto.")
    with timings:
        variances = dict(result.variances) if pert else {}
        rows = []
        for t in schedule.timings:
            row = {"Actividad": t.id, "Estado": "★ Crítica" if t.critical else "Con holgura", "Duración": t.duration,
                   "IC": t.early_start, "TC": t.early_finish, "IL": t.late_start, "TL": t.late_finish,
                   "Holgura": t.slack, "Crítica": t.critical}
            if pert:
                row["Varianza"] = variances[t.id]
            rows.append(row)
        _table(rows, "tiempos_proyecto.csv")
        st.caption("IC/TC: inicio y terminación cercanos. IL/TL: inicio y terminación lejanos.")
    with gantt:
        chart(gantt_figure(schedule), "gantt")
        st.caption("★ y barras rayadas: actividades críticas. Tramo punteado: margen de holgura.")
    with steps:
        section("03", "Recorridos de planificación")
        count = step_controls(len(schedule.steps), "explore_project_step")
        current = schedule.steps[count - 1] if count else None
        if current:
            note(f"Recorrido hacia {'adelante' if current.phase == 'Adelante' else 'atrás'} · {current.activity}",
                 f"Inicio: {current.start:g} · Terminación: {current.finish:g}. "
                 + ("Se calculan tiempos cercanos." if current.phase == "Adelante" else "Se calculan tiempos lejanos."))
        else:
            note("Estado inicial", "Aún no se han calculado los tiempos de las actividades.")
        chart(project_figure(project, schedule, focus_node=current.activity if current else None), "project_steps")
        st.caption("Se muestra la red final con la actividad del paso actual en ámbar. La tabla acumula solo los tiempos ya calculados.")
        _table([{"Recorrido": s.phase, "Actividad": s.activity, "Inicio": s.start, "Terminación": s.finish}
                for s in schedule.steps[:count]], "paso_proyecto.csv", download=False)
        with st.expander("Registro completo y descarga"):
            _table([{"Recorrido": s.phase, "Actividad": s.activity, "Inicio": s.start, "Terminación": s.finish}
                    for s in schedule.steps], "procedimiento_proyecto.csv")
