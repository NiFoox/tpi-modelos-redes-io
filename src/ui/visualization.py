"""Representación interactiva; NetworkX solo calcula posiciones de dibujo."""

from html import escape
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from src.core import Graph


@st.cache_data(show_spinner=False)
def _positions(nodes, pairs):
    drawing = nx.Graph()
    drawing.add_nodes_from(nodes)
    drawing.add_edges_from(pairs)
    return {n: tuple(p) for n, p in nx.spring_layout(drawing, seed=42, iterations=50).items()}


def network_figure(graph: Graph, *, selected=(), selected_nodes=(), labels=None, positions=None, project=False):
    pairs = tuple((e.source, e.target) for e in graph.edges)
    positions = positions or _positions(graph.nodes, pairs)
    selected = set(selected)
    if not graph.directed:
        selected |= {(v, u) for u, v in selected}
    figure = go.Figure()
    annotations, label_x, label_y, label_text, hover_text = [], [], [], [], []
    show_labels = len(pairs) <= 80
    lines = {False: ([], []), True: ([], [])}
    for edge in graph.edges:
        u, v = edge.source, edge.target
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        dx, dy = x1 - x0, y1 - y0
        # Separa visualmente las dos orientaciones si ambas existen.
        bend = 0.15 if graph.directed and (v, u) in pairs else 0
        mx, my = (x0 + x1) / 2 - dy * bend, (y0 + y1) / 2 + dx * bend
        curve = [((1-t)**2*x0 + 2*(1-t)*t*mx + t*t*x1,
                  (1-t)**2*y0 + 2*(1-t)*t*my + t*t*y1)
                 for t in [i / 12 for i in range(13)]]
        active = (u, v) in selected
        xs, ys = lines[active]
        xs.extend([p[0] for p in curve] + [None])
        ys.extend([p[1] for p in curve] + [None])
        value = (labels or {}).get((u, v), edge.weight if edge.weight is not None else edge.capacity)
        label_x.append(curve[6][0])
        label_y.append(curve[6][1])
        label_text.append(escape(str(value)) if show_labels and not project else "")
        hover_text.append(f"{escape(u)} → {escape(v)}: {escape(str(value))}")
        if graph.directed:
            ax, ay = curve[7]
            tx, ty = curve[9]
            annotations.append(dict(x=tx, y=ty, ax=ax, ay=ay, xref="x", yref="y",
                                    axref="x", ayref="y", text="", showarrow=True,
                                    arrowhead=2, arrowsize=1.3, arrowwidth=1.4,
                                    arrowcolor="#0D9488" if active else "#94A3B8"))
    for active, (xs, ys) in lines.items():
        figure.add_trace(go.Scatter(x=xs, y=ys, mode="lines", hoverinfo="skip",
                                   line=dict(color="#0D9488" if active else "#CBD5E1",
                                             width=3.5 if active else 1.5)))
    figure.add_trace(go.Scatter(x=label_x, y=label_y, text=label_text,
                               customdata=hover_text, mode="markers+text", textposition="top center",
                               marker=dict(size=9, color="rgba(0,0,0,0)"),
                               hovertemplate="%{customdata}<extra></extra>"))
    nodes = graph.nodes
    active_nodes = set(selected_nodes) | {n for pair in selected for n in pair}
    figure.add_trace(go.Scatter(
        x=[positions[n][0] for n in nodes], y=[positions[n][1] for n in nodes],
        mode="markers+text", text=[escape(n) for n in nodes],
        textposition="middle center" if project else "top center",
        customdata=[escape(str((labels or {}).get(n, n))) for n in nodes],
        marker=dict(size=34 if project else 18, symbol="square" if project else "circle",
                    color=["#99F6E4" if n in active_nodes else "#DBEAFE" for n in nodes],
                    line=dict(color="#0D9488", width=1.5)),
        hovertemplate="%{customdata}<extra></extra>",
    ))
    figure.update_layout(height=520, margin=dict(l=25, r=25, t=30, b=25),
                         showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)", annotations=annotations,
                         xaxis=dict(visible=False),
                         yaxis=dict(visible=False, scaleanchor="x", scaleratio=1))
    return figure


def project_figure(project, result):
    graph = Graph(directed=True)
    levels, positions, labels = {}, {}, {}
    activities = {a.id: a for a in project.activities}
    per_level = {}
    for timing in result.timings:
        node = timing.id
        levels[node] = 1 + max((levels[p] for p in activities[node].predecessors), default=-1)
        row = per_level.get(levels[node], 0)
        per_level[levels[node]] = row + 1
        positions[node] = (levels[node] * 2, -row * 1.5)
        graph.add_node(node)
        labels[node] = (f"{node} | duración: {timing.duration:g} | IC: {timing.early_start:g} | "
                        f"TC: {timing.early_finish:g} | holgura: {timing.slack:g}")
        for predecessor in activities[node].predecessors:
            graph.add_edge(predecessor, node, weight=0)
    return network_figure(graph, selected=result.critical_edges,
                          selected_nodes=result.critical_activities, positions=positions,
                          labels=labels, project=True)


def gantt_figure(result):
    figure = go.Figure()
    for critical, name, color in [(True, "Crítica", "#0D9488"), (False, "Con holgura", "#94A3B8")]:
        rows = [t for t in result.timings if t.critical == critical]
        figure.add_trace(go.Bar(y=[escape(t.id) for t in rows], x=[t.duration for t in rows],
                               base=[t.early_start for t in rows], orientation="h", name=name,
                               marker_color=color, hovertemplate="%{y}: inicio %{base}, duración %{x}<extra></extra>"))
    figure.update_layout(barmode="overlay", height=max(320, min(900, 28 * len(result.timings))),
                         xaxis_title="Tiempo (unidad del proyecto)", yaxis=dict(autorange="reversed"),
                         margin=dict(l=20, r=20, t=20, b=20))
    return figure
