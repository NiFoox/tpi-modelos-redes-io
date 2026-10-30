"""Visualizaciones de Plotly; NetworkX se usa solo para posicionamiento."""
from html import escape

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from src.core import Graph
from .theme import ACCENT, AMBER, CYAN, MUTED


@st.cache_data(show_spinner=False, max_entries=24)
def _positions(nodes, pairs):
    drawing = nx.Graph()
    drawing.add_nodes_from(nodes)
    drawing.add_edges_from(pairs)
    return {n: tuple(p) for n, p in nx.spring_layout(drawing, seed=42, iterations=50).items()}


def _layout(figure, *, height=510, identity="network"):
    figure.update_layout(
        template="plotly_dark", height=height, margin=dict(l=30, r=30, t=25, b=25),
        font=dict(family="Arial, sans-serif", color="#D9E6F5", size=12),
        paper_bgcolor="#111D2E", plot_bgcolor="#111D2E",
        hoverlabel=dict(bgcolor="#1C3046", bordercolor="#46617C", font_color="#EDF3FC"),
        uirevision=identity, dragmode="pan", showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
    )
    return figure


def edge_curve(positions, source, target, reciprocal=False):
    """Coordenadas de una arista, incluida la separación de arcos opuestos."""
    x0, y0 = positions[source]
    x1, y1 = positions[target]
    dx, dy = x1 - x0, y1 - y0
    bend = .24 if reciprocal else 0
    mx, my = (x0 + x1) / 2 - dy * bend, (y0 + y1) / 2 + dx * bend
    return [((1-t)**2*x0 + 2*(1-t)*t*mx + t*t*x1,
             (1-t)**2*y0 + 2*(1-t)*t*my + t*t*y1)
            for t in [i / 12 for i in range(13)]]


def network_figure(graph: Graph, *, selected=(), selected_nodes=(), labels=None,
                   positions=None, project=False, focus=(), focus_node=None, roles=None):
    pairs = tuple((e.source, e.target) for e in graph.edges)
    pair_set = set(pairs)
    positions = positions if positions is not None else _positions(graph.nodes, pairs)
    selected, focus = set(selected), set(focus)
    if not graph.directed:
        selected |= {(v, u) for u, v in selected}
        focus |= {(v, u) for u, v in focus}
    figure = go.Figure()
    annotations, label_x, label_y, hover_text = [], [], [], []
    show_labels = len(pairs) <= 55 and not project
    # Tres trazas de aristas mantienen el costo de renderizado acotado.
    lines = {"base": ([], []), "selected": ([], []), "focus": ([], [])}
    for edge in graph.edges:
        u, v = edge.source, edge.target
        curve = edge_curve(positions, u, v, graph.directed and (v, u) in pair_set)
        state = "focus" if (u, v) in focus else "selected" if (u, v) in selected else "base"
        xs, ys = lines[state]
        xs.extend([p[0] for p in curve] + [None])
        ys.extend([p[1] for p in curve] + [None])
        color = AMBER if state == "focus" else ACCENT if state == "selected" else "#60748D"
        value = (labels or {}).get((u, v), edge.weight if edge.weight is not None else edge.capacity)
        lx, ly = curve[6]
        label_x.append(lx)
        label_y.append(ly)
        relation = "→" if graph.directed else "—"
        hover_text.append(f"<b>{escape(u)} {relation} {escape(v)}</b><br>"
                         f"{'Precedencia' if project else 'Valor: ' + escape(str(value))}")
        if show_labels:
            annotations.append(dict(x=lx, y=ly, text=escape(str(value)), showarrow=False,
                                    font=dict(color="#E0ECF8", size=11), bgcolor="#152437",
                                    bordercolor="#32465F", borderpad=3, borderwidth=1))
        if graph.directed:
            ax, ay = curve[7]
            tx, ty = curve[9]
            annotations.append(dict(x=tx, y=ty, ax=ax, ay=ay, xref="x", yref="y",
                                    axref="x", ayref="y", text="", showarrow=True,
                                    arrowhead=3, arrowsize=1.2, arrowwidth=1.6, arrowcolor=color))
    for state, (xs, ys) in lines.items():
        figure.add_trace(go.Scatter(x=xs, y=ys, mode="lines", hoverinfo="skip",
                                   line=dict(color=AMBER if state == "focus" else ACCENT if state == "selected" else "#53657D",
                                             width=3.4 if state != "base" else 1.3,
                                             dash="dot" if state == "focus" else "solid")))
    figure.add_trace(go.Scatter(x=label_x, y=label_y, customdata=hover_text, mode="markers",
                               marker=dict(size=18, color="rgba(0,0,0,0)"),
                               hovertemplate="%{customdata}<extra></extra>"))
    nodes = graph.nodes
    active_nodes = set(selected_nodes)
    if not project:
        active_nodes |= {n for pair in selected for n in pair}
    roles = roles or {}
    compact = len(nodes) > 60
    symbols, texts, colors, sizes, hover = [], [], [], [], []
    for n in nodes:
        critical = project and n in active_nodes
        texts.append(("★ " if critical else "") + escape(n))
        symbols.append("diamond" if critical or roles.get(n) == "Origen" else "square" if roles.get(n) == "Destino" else "circle")
        colors.append(AMBER if n == focus_node else "#206B60" if n in active_nodes else "#233B55")
        sizes.append(42 if project else 15 if compact else 26)
        detail = escape(str((labels or {}).get(n, n)))
        hover.append(f"<b>{detail}</b>" + (f"<br>{escape(roles[n])}" if n in roles else "") +
                     ("<br>★ Actividad crítica · holgura cero" if critical else ""))
    figure.add_trace(go.Scatter(
        x=[positions[n][0] for n in nodes], y=[positions[n][1] for n in nodes],
        mode="markers+text" if not compact else "markers", text=texts,
        textposition="middle center" if project else "top center",
        textfont=dict(color="#EDF3FC", size=12), customdata=hover,
        marker=dict(size=sizes, symbol=symbols, color=colors,
                    line=dict(color=[AMBER if n == focus_node else ACCENT if n in active_nodes else "#6B89AB" for n in nodes], width=1.7)),
        hovertemplate="%{customdata}<extra></extra>",
    ))
    # La identidad depende de la topología: al avanzar pasos conserva zoom y posición.
    return _layout(figure, identity=repr((nodes, pairs, project))).update_layout(annotations=annotations)


def _project_layout(project):
    """Posiciona un DAG sin resolver tiempos ni rutas críticas."""
    drawing = nx.DiGraph()
    drawing.add_nodes_from(a.id for a in project.activities)
    drawing.add_edges_from((p, a.id) for a in project.activities for p in a.predecessors)
    # El posicionamiento también debe ser seguro antes de validar la aciclicidad.
    if not nx.is_directed_acyclic_graph(drawing):
        return _positions(tuple(drawing.nodes), tuple(drawing.edges))
    positions = {}
    for level, nodes in enumerate(nx.topological_generations(drawing)):
        nodes = list(nodes)
        for row, node in enumerate(nodes):
            positions[node] = (level * 2, (len(nodes) - 1) * .8 - row * 1.6)
    return positions


def _project_graph(project):
    graph = Graph(directed=True)
    for activity in project.activities:
        graph.add_node(activity.id)
        for predecessor in activity.predecessors:
            graph.add_edge(predecessor, activity.id, weight=0)
    return graph


def project_preview(project):
    return network_figure(_project_graph(project), positions=_project_layout(project), project=True)


def project_figure(project, result, *, focus_node=None):
    labels = {t.id: (f"{t.id} | duración: {t.duration:g} | IC: {t.early_start:g} | "
                     f"TC: {t.early_finish:g} | IL: {t.late_start:g} | TL: {t.late_finish:g} | holgura: {t.slack:g}")
              for t in result.timings}
    return network_figure(_project_graph(project), selected=result.critical_edges,
                          selected_nodes=result.critical_activities, positions=_project_layout(project),
                          labels=labels, project=True, focus_node=focus_node)


def gantt_figure(result):
    figure = go.Figure()
    for critical, name, color in [(True, "★ Crítica", ACCENT), (False, "Con holgura", CYAN)]:
        rows = [t for t in result.timings if t.critical == critical]
        figure.add_trace(go.Bar(
            y=[("★ " if t.critical else "") + escape(t.id) for t in rows],
            x=[t.duration for t in rows], base=[t.early_start for t in rows], orientation="h", name=name,
            marker=dict(color=color, pattern_shape="/" if critical else ""),
            customdata=[[t.early_finish, t.slack] for t in rows],
            hovertemplate="<b>%{y}</b><br>Inicio: %{base}<br>Duración: %{x}<br>Fin: %{customdata[0]}<br>Holgura: %{customdata[1]}<extra></extra>"))
    rows = [t for t in result.timings if t.slack > 0]
    figure.add_trace(go.Bar(
        y=[escape(t.id) for t in rows], x=[t.slack for t in rows],
        base=[t.early_finish for t in rows], orientation="h", name="Margen de holgura",
        marker=dict(color="rgba(99,199,244,.14)", line=dict(color=CYAN, width=1), pattern_shape="."),
        hovertemplate="%{y}<br>Holgura: %{x}<extra></extra>"))
    _layout(figure, height=max(350, min(900, 40 * len(result.timings))), identity=repr(result.timings))
    figure.update_layout(
        barmode="overlay", showlegend=True, legend=dict(orientation="h", y=1.15),
        xaxis=dict(visible=True, title="Tiempo · unidad del proyecto", gridcolor="#26384D", zeroline=False),
        yaxis=dict(visible=True, autorange="reversed", scaleanchor=None,
                   categoryorder="array", categoryarray=[("★ " if t.critical else "") + escape(t.id) for t in result.timings]),
        margin=dict(l=20, r=20, t=55, b=45))
    return figure
