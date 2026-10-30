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
    """Ocupa el espacio nativo del logo, en lugar de añadir otra cabecera."""
    icon = '<rect x="1" y="1" width="34" height="34" rx="9" fill="#173a37" stroke="#2d5b53"/>'
    icon += '<path d="M10 11h16M10 25h16M11 10v16M25 10v16" stroke="#42d6bd" stroke-width="2"/>'
    icon += '<circle cx="18" cy="18" r="5" fill="#173a37" stroke="#42d6bd" stroke-width="2"/>'
    image = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 238 36">'
             '<title>Modelos de Redes · Investigación Operativa</title>' + icon +
             '<text x="44" y="16" fill="#edf3fc" font-family="Arial,sans-serif" '
             'font-size="16" font-weight="bold">Modelos de Redes</text>'
             '<text x="44" y="30" fill="#92a5be" font-family="Arial,sans-serif" '
             'font-size="7.6" letter-spacing=".9">INVESTIGACIÓN OPERATIVA</text></svg>')
    compact = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36">' + icon + '</svg>'
    st.logo(image, size="large", icon_image=compact)


def hero(algorithm, area):
    category, description = DESCRIPTIONS[algorithm]
    st.html(f'''<div class="hero" role="banner"><div class="eyebrow">ESPACIO DE ANÁLISIS <span>/</span> {escape(area.upper())}</div>
        <div class="hero-title"><h1>{escape(algorithm)}</h1><span class="pill">{escape(category)}</span></div>
        <p>{escape(description)}</p></div>''')


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
