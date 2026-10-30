"""Identidad visual y componentes compartidos de la interfaz."""
from html import escape
from pathlib import Path

import streamlit as st

ACCENT = "#42D6BD"
CYAN = "#63C7F4"
AMBER = "#F3BC6B"
MUTED = "#8D9DB3"
PLOT_CONFIG = {
    "displaylogo": False, "scrollZoom": True, "responsive": True,
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    "toImageButtonOptions": {"filename": "modelos_de_redes", "scale": 2},
}
DESCRIPTIONS = {
    "Prim": ("Árbol de expansión mínima", "Conectá todos los nodos al menor costo, expandiendo un árbol desde un nodo inicial."),
    "Kruskal": ("Árbol de expansión mínima", "Explorá las conexiones de menor a mayor peso y construí un árbol sin ciclos."),
    "Dijkstra": ("Camino más corto", "Encontrá la ruta de menor distancia entre dos nodos con pesos no negativos."),
    "Flujo máximo": ("Capacidad de una red", "Calculá cuánto puede transportar una red entre una fuente y un sumidero. Ford-Fulkerson · Edmonds-Karp."),
    "CPM": ("Planificación determinista", "Organizá actividades, calculá holguras e identificá las rutas que determinan la duración del proyecto."),
    "PERT": ("Planificación probabilística", "Trabajá con tiempos optimistas, probables y pesimistas para estimar la duración y su variabilidad."),
}


def apply_theme():
    st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")


def brand():
    st.html('''<div class="brand"><span class="brand-mark">⌘</span><div>Modelos de Redes<small>INVESTIGACIÓN OPERATIVA</small></div></div>''')


def hero(algorithm, area):
    category, description = DESCRIPTIONS[algorithm]
    st.html(f'''<header class="hero"><div class="eyebrow">ESPACIO DE ANÁLISIS <span>/</span> {escape(area.upper())}</div>
        <div class="hero-title"><h1>{escape(algorithm)}</h1><span class="pill">{escape(category)}</span></div>
        <p>{escape(description)}</p></header>''')


def section(number, title, subtitle=None):
    st.html(f'<div class="section-title"><span>{escape(number)}</span><h3>{escape(title)}</h3></div>')
    if subtitle:
        st.caption(subtitle)


def note(title, body, *, tone="neutral"):
    st.html(f'<div class="insight {escape(tone)}"><strong>{escape(title)}</strong><p>{escape(body)}</p></div>')


def legend(project=False):
    label = "★ Actividad crítica" if project else "Conexión seleccionada"
    st.html(f'<div class="graph-legend"><span><i class="selected"></i>{label}</span>'
            '<span><i></i>Red original</span><span>Arrastrá para mover · Rueda para zoom · Doble clic para ajustar</span></div>')


def metrics(items):
    for index, (column, (label, value)) in enumerate(zip(st.columns(len(items)), items)):
        with column, st.container(key=f"metric_{index}", border=True):
            st.metric(label, value)


def chart(figure, key):
    st.plotly_chart(figure, use_container_width=True, theme=None, config=PLOT_CONFIG, key=key)


def _move_step(key, value):
    st.session_state[key] = value


def step_controls(total, key):
    """Navegación de un registro real; no vuelve a ejecutar el algoritmo."""
    if not total:
        return 0
    if key not in st.session_state:
        st.session_state[key] = total
    current = min(total, max(0, st.session_state[key]))
    controls = st.columns([1, 1, 1, 1])
    for column, label, value, disabled in [
        (controls[0], "Inicio", 0, current == 0),
        (controls[1], "← Anterior", current - 1, current == 0),
        (controls[2], "Siguiente →", current + 1, current == total),
        (controls[3], "Final", total, current == total),
    ]:
        column.button(label, key=f"{key}_{label}", on_click=_move_step,
                      args=(key, value), disabled=disabled, use_container_width=True)
    current = st.slider("Paso del procedimiento", 0, total, key=key)
    st.progress(current / total, text=f"{current} de {total} pasos registrados")
    return current
