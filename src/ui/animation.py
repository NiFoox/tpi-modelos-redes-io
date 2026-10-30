"""Reproducción de registros existentes en un componente Plotly aislado.

El navegador recibe la topología una vez y eventos compactos, no una copia
completa del gráfico por fotograma. No vuelve a ejecutar los algoritmos.
"""
from functools import lru_cache
import json
from pathlib import Path

from plotly.offline import get_plotlyjs
import streamlit.components.v1 as components

from src.algorithms.mst import MSTResult
from src.algorithms.shortest_path import ShortestPathResult
from .visualization import (
    _positions, _project_graph, _project_layout, edge_curve,
    network_figure, project_figure, project_preview,
)


def _topology(graph, positions, figure):
    pairs = {(e.source, e.target) for e in graph.edges}
    show_labels = len(graph.edges) <= 55
    return {
        "figure": figure.to_plotly_json(), "nodes": list(graph.nodes),
        "directed": graph.directed,
        "edges": [{"source": e.source, "target": e.target,
                   "curve": edge_curve(positions, e.source, e.target, graph.directed and (e.target, e.source) in pairs),
                   "weight": e.weight, "capacity": e.capacity,
                   "label": i * (2 if graph.directed else 1) if show_labels else None}
                  for i, e in enumerate(graph.edges)],
    }


def graph_playback(graph, result, *, start_node=None):
    positions = _positions(graph.nodes, tuple((e.source, e.target) for e in graph.edges))
    roles = {}
    if isinstance(result, ShortestPathResult):
        roles = {result.source: "Origen", result.target: "Destino"}
    elif not isinstance(result, MSTResult):
        roles = {result.source: "Origen", result.sink: "Destino"}
    payload = _topology(graph, positions, network_figure(graph, positions=positions, roles=roles))
    lookup = {(e.source, e.target): i for i, e in enumerate(graph.edges)}
    if not graph.directed:
        lookup.update({(e.target, e.source): i for i, e in enumerate(graph.edges)})
    events = []
    if isinstance(result, MSTResult):
        payload["kind"] = "mst"
        visited = {start_node or min(graph.nodes)}
        for step in result.steps:
            u, v = step.edge.source, step.edge.target
            if result.algorithm == "Prim" and v in visited and u not in visited:
                u, v = v, u
            if step.accepted:
                visited.update((u, v))
            edge = lookup[u, v]
            events.append({"edge": edge, "accepted": step.accepted,
                           "path": [{"edge": edge, "reverse": u != graph.edges[edge].source}]
                                   if result.algorithm == "Prim" and step.accepted else [],
                           "title": "Conexión aceptada" if step.accepted else "Conexión descartada",
                           "text": f"{u} — {v} · Peso {step.edge.weight:g}. {step.reason}. Costo acumulado: {step.accumulated_weight:g}."})
        payload["final_text"] = f"Árbol mínimo · Costo {result.total_weight:g} · {len(result.selected_edges)} aristas."
    elif isinstance(result, ShortestPathResult):
        payload.update(kind="dijkstra", source=result.source)
        for step in result.steps:
            edge = lookup[step.source, step.target]
            previous = "∞" if step.previous_distance == float("inf") else f"{step.previous_distance:g}"
            events.append({"edge": edge, "accepted": step.accepted,
                           "source": step.source, "target": step.target, "distance": step.candidate_distance,
                           "path": [{"edge": edge, "reverse": step.source != graph.edges[edge].source}],
                           "title": "Distancia actualizada" if step.accepted else "Se conserva la distancia",
                           "text": f"{step.source} → {step.target} · Anterior: {previous} · Candidata: {step.candidate_distance:g}."})
        payload["final_edges"] = [lookup[u, v] for u, v in zip(result.path, result.path[1:])]
        payload["final_text"] = (f"Ruta: {' → '.join(result.path)} · Distancia {result.distance:g}." if result.reachable
                                 else "El destino es inalcanzable desde el origen.")
    else:
        payload.update(kind="flow", source=result.source)
        for step in result.steps:
            path = []
            for (u, v), direction in zip(zip(step.path, step.path[1:]), step.directions):
                reverse = direction != "Directo"
                path.append({"edge": lookup[v, u] if reverse else lookup[u, v], "reverse": reverse, "cancel": reverse})
            events.append({"path": path, "amount": step.augmentation,
                           "title": "Camino aumentante",
                           "text": f"{' → '.join(step.path)} · Aumento {step.augmentation:g} · Flujo acumulado {step.total_flow:g}. "
                                   + " · ".join(step.directions)})
        payload["final_text"] = f"Flujo máximo {result.total_flow:g} · Capacidad del corte mínimo {result.cut_capacity:g}."
    payload["events"] = events
    return payload


def project_playback(project, schedule):
    graph = _project_graph(project)
    payload = _topology(graph, _project_layout(project), project_preview(project))
    payload.update(kind="project", final_text=f"Duración {schedule.duration:g} · Ruta crítica: {' → '.join(schedule.critical_path)}.")
    payload["events"] = [{"node": s.activity, "phase": s.phase,
                          "title": f"Recorrido hacia {'adelante' if s.phase == 'Adelante' else 'atrás'} · {s.activity}",
                          "text": f"Inicio: {s.start:g} · Terminación: {s.finish:g}. "
                                  + ("Tiempos cercanos." if s.phase == "Adelante" else "Tiempos lejanos.")}
                         for s in schedule.steps]
    final = project_figure(project, schedule)
    payload["final_nodes"] = final.data[-1].to_plotly_json()
    critical = set(schedule.critical_edges)
    payload["final_edges"] = [i for i, e in enumerate(graph.edges) if (e.source, e.target) in critical]
    return payload


@lru_cache(maxsize=1)
def _template():
    return Path(__file__).with_name("playback.html").read_text(encoding="utf-8").replace("__PLOTLY_SOURCE__", get_plotlyjs())


def playback_html(payload):
    # No interpola identificadores del usuario en HTML ni en código ejecutable.
    from plotly.utils import PlotlyJSONEncoder
    data = json.dumps(payload, cls=PlotlyJSONEncoder, ensure_ascii=False, allow_nan=False)
    for literal, escaped in [("&", "\\u0026"), ("<", "\\u003c"), (">", "\\u003e"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")]:
        data = data.replace(literal, escaped)
    return _template().replace("__PLAYBACK_DATA__", data)


def render_playback(payload):
    components.html(playback_html(payload), height=650, scrolling=False, tab_index=0)
