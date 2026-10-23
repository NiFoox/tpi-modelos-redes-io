"""Editores tabulares, ejemplos y archivos de entrada."""

import random

import pandas as pd
import streamlit as st

from src.services.data_io import (
    graph_from_rows, graph_csv, project_from_rows, project_csv, read_csv,
)


def _graph_defaults(flow):
    edges = ([("S", "A", 10), ("S", "B", 8), ("A", "B", 3),
              ("A", "T", 7), ("B", "T", 10)] if flow else
             [("A", "B", 1), ("B", "C", 2), ("A", "C", 3), ("C", "D", 4), ("A", "D", 9)])
    field = "capacidad" if flow else "peso"
    return [{"origen": u, "destino": v, field: value} for u, v, value in edges]


def _edge_frame(rows):
    frame = pd.DataFrame(rows, columns=["origen", "destino", "peso", "capacidad"])
    for col in ["origen", "destino"]:
        frame[col] = frame[col].astype("string")
    for col in ["peso", "capacidad"]:
        frame[col] = pd.to_numeric(frame[col], errors="raise").astype(float)
    return frame


def graph_input(algorithm):
    flow = algorithm == "Flujo máximo"
    family = "flow" if flow else "weighted"
    base_key, revision_key, nodes_key = f"{family}_data", f"{family}_revision", f"{family}_nodes"
    if base_key not in st.session_state:
        st.session_state[base_key] = _edge_frame(_graph_defaults(flow))
        st.session_state[revision_key] = 0
        st.session_state[nodes_key] = ""

    st.subheader("1. Definí la red")
    directed = (True if flow else st.checkbox("Red dirigida", value=False, key="directed"))
    if flow:
        st.caption("Las conexiones tienen orientación y capacidad. Fuente y sumidero se eligen debajo.")
    with st.expander("Ejemplos, CSV y redes grandes"):
        col1, col2 = st.columns(2)
        if col1.button("Cargar ejemplo", key=f"example_{family}"):
            st.session_state[base_key] = _edge_frame(_graph_defaults(flow))
            st.session_state[nodes_key] = ""
            st.session_state[revision_key] += 1
        if col2.button("Vaciar red", key=f"clear_{family}"):
            st.session_state[base_key] = _edge_frame([])
            st.session_state[nodes_key] = ""
            st.session_state[revision_key] += 1
        n = st.number_input("Nodos a generar", min_value=2, max_value=1000, value=200,
                            step=1, key=f"size_{family}")
        seed = st.number_input("Semilla", min_value=0, value=42, step=1, key=f"seed_{family}")
        if st.button("Generar red conectada", key=f"generate_{family}"):
            rng = random.Random(seed)
            names = [f"N{i + 1}" for i in range(n)]
            pairs = {(names[i], names[i + 1]) for i in range(n - 1)}
            for _ in range(2 * n):
                i, j = sorted(rng.sample(range(n), 2))
                pairs.add((names[i], names[j]))
            field = "capacidad" if flow else "peso"
            rows = [{"origen": u, "destino": v, field: rng.randint(1, 30)}
                    for u, v in sorted(pairs)]
            st.session_state[base_key] = _edge_frame(rows)
            st.session_state[nodes_key] = "\n".join(names)
            st.session_state[revision_key] += 1
        upload = st.file_uploader("Importar conexiones CSV (UTF-8)", type="csv", key=f"upload_{family}")
        st.caption("Columnas: origen,destino,peso o capacidad. Opcional: tipo=nodo/arista. "
                   "El archivo exportado conserva nodos aislados. Seleccioná aquí la orientación de la red.")
        if st.button("Aplicar CSV", disabled=upload is None, key=f"apply_{family}"):
            try:
                rows = read_csv(upload.getvalue(), {"origen", "destino"}, {"tipo", "peso", "capacidad"})
                loaded = graph_from_rows(rows, directed=directed)
                st.session_state[base_key] = _edge_frame([
                    {"origen": e.source, "destino": e.target, "peso": e.weight, "capacidad": e.capacity}
                    for e in loaded.edges])
                st.session_state[nodes_key] = "\n".join(loaded.nodes)
                st.session_state[revision_key] += 1
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
    st.text_area("Nodos explícitos (uno por línea; opcional)", key=nodes_key, height=100,
                 help="Los extremos de cada conexión se crean automáticamente. Usá este campo para nodos aislados.")
    metric = "capacidad" if flow else "peso"
    edited = st.data_editor(
        st.session_state[base_key], num_rows="dynamic", hide_index=True, width="stretch",
        column_order=["origen", "destino", metric],
        column_config={"origen": st.column_config.TextColumn("Origen", required=True),
                       "destino": st.column_config.TextColumn("Destino", required=True),
                       "peso": st.column_config.NumberColumn("Peso", format="%.6g"),
                       "capacidad": st.column_config.NumberColumn("Capacidad", min_value=0, format="%.6g")},
        key=f"edges_{family}_{st.session_state[revision_key]}",
    )
    st.caption("Agregá filas al final. Para borrarlas, seleccioná las filas y usá la papelera del editor.")
    nodes = [line.strip() for line in st.session_state[nodes_key].splitlines() if line.strip()]
    graph = graph_from_rows(edited.to_dict("records"), directed=directed, nodes=nodes)
    st.download_button("Descargar red CSV", graph_csv(graph), "red.csv", "text/csv", key="download_graph")
    return graph


def _project_defaults(pert):
    data = [("A", "", 1, 2, 3), ("B", "", 2, 3, 4), ("C", "A", 1, 2, 3),
            ("D", "B", 2, 4, 6), ("E", "C", 1, 4, 7), ("F", "C", 1, 2, 9),
            ("G", "D;E", 3, 4, 11), ("H", "F;G", 1, 2, 3)]
    return [dict(actividad=n, predecesoras=p, **(
        dict(optimista=a, probable=m, pesimista=b) if pert else dict(duracion=(a + 4*m + b)/6)))
        for n, p, a, m, b in data]


def _activity_frame(rows, pert):
    numeric = ["optimista", "probable", "pesimista"] if pert else ["duracion"]
    frame = pd.DataFrame(rows, columns=["actividad", "predecesoras"] + numeric)
    for col in ["actividad", "predecesoras"]:
        frame[col] = frame[col].astype("string").fillna("")
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col], errors="raise").astype(float)
    return frame


def project_input(pert):
    family = "pert" if pert else "cpm"
    base, rev = f"{family}_data", f"{family}_revision"
    if base not in st.session_state:
        st.session_state[base] = _activity_frame(_project_defaults(pert), pert)
        st.session_state[rev] = 0
    st.subheader("1. Definí las actividades")
    st.caption("Predecesoras inmediatas separadas por ; (ejemplo: A;B). "
               "Dejá la celda vacía si la actividad puede comenzar al inicio.")
    with st.expander("Ejemplo y archivos CSV"):
        if st.button("Cargar General Foundry", key=f"example_{family}"):
            st.session_state[base] = _activity_frame(_project_defaults(pert), pert)
            st.session_state[rev] += 1
        if st.button("Vaciar proyecto", key=f"clear_{family}"):
            st.session_state[base] = _activity_frame([], pert)
            st.session_state[rev] += 1
        upload = st.file_uploader("Importar actividades CSV", type="csv", key=f"upload_{family}")
        fields = {"actividad", "predecesoras"} | ({"optimista", "probable", "pesimista"} if pert else {"duracion"})
        st.caption("Columnas: " + ", ".join(sorted(fields)) + ". Usá punto decimal.")
        if st.button("Aplicar CSV", disabled=upload is None, key=f"apply_{family}"):
            try:
                rows = read_csv(upload.getvalue(), fields)
                project_from_rows(rows, pert=pert)
                st.session_state[base] = _activity_frame(rows, pert)
                st.session_state[rev] += 1
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
    numeric = ["optimista", "probable", "pesimista"] if pert else ["duracion"]
    config = {name: st.column_config.NumberColumn(name.capitalize(), min_value=0, required=True)
              for name in numeric}
    config["actividad"] = st.column_config.TextColumn("Actividad", required=True)
    config["predecesoras"] = st.column_config.TextColumn("Predecesoras")
    edited = st.data_editor(st.session_state[base], num_rows="dynamic", hide_index=True,
                            width="stretch", column_config=config,
                            key=f"activities_{family}_{st.session_state[rev]}")
    project = project_from_rows(edited.to_dict("records"), pert=pert)
    st.download_button("Descargar actividades CSV", project_csv(project, pert=pert),
                        f"{family}.csv", "text/csv", key="download_project")
    return project
