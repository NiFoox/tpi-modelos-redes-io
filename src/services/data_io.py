"""Formatos tabulares independientes de la interfaz y de pandas."""

import csv
from io import StringIO
from math import isnan

from src.core import Graph
from src.core.activity import Activity, Project


def text_value(value) -> str:
    if value is None or isinstance(value, float) and isnan(value):
        return ""
    return str(value).strip()


def number_value(value):
    text = text_value(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError(f"El valor {text!r} no es un número; use punto decimal.") from exc


def graph_from_rows(rows, *, directed: bool, nodes=()) -> Graph:
    graph = Graph(directed=directed)
    for node in nodes:
        graph.add_node(node)
    for i, row in enumerate(rows, 1):
        if not any(text_value(v) for v in row.values()):
            continue
        try:
            kind = text_value(row.get("tipo")).lower() or "arista"
            u, v = text_value(row.get("origen")), text_value(row.get("destino"))
            if kind == "nodo":
                if v or text_value(row.get("peso")) or text_value(row.get("capacidad")):
                    raise ValueError("Una fila de nodo solo debe incluir su identificador en origen.")
                graph.add_node(u)
            elif kind == "arista":
                graph.add_edge(u, v, weight=number_value(row.get("peso")),
                               capacity=number_value(row.get("capacidad")))
            else:
                raise ValueError("El tipo debe ser nodo o arista.")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Fila {i}: {exc}") from exc
    return graph


def project_from_rows(rows, *, pert: bool) -> Project:
    activities = []
    for i, row in enumerate(rows, 1):
        if not any(text_value(v) for v in row.values()):
            continue
        try:
            identifier = text_value(row.get("actividad"))
            if ";" in identifier:
                raise ValueError("El identificador de actividad no puede contener punto y coma.")
            raw = text_value(row.get("predecesoras"))
            predecessors = tuple(p.strip() for p in raw.split(";")) if raw else ()
            if pert:
                kwargs = {"optimistic": number_value(row.get("optimista")),
                          "most_likely": number_value(row.get("probable")),
                          "pessimistic": number_value(row.get("pesimista"))}
            else:
                kwargs = {"duration": number_value(row.get("duracion"))}
                if kwargs["duration"] is None:
                    raise ValueError("Falta la duración de la actividad.")
            activities.append(Activity(identifier, predecessors, **kwargs))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Fila {i}: {exc}") from exc
    return Project(tuple(activities))


def read_csv(data: bytes | str, required: set[str], optional: set[str] | None = None):
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("El CSV debe estar codificado en UTF-8.") from exc
    reader = csv.DictReader(StringIO(data.lstrip("\ufeff")), strict=True)
    try:
        fields = reader.fieldnames
    except csv.Error as exc:
        raise ValueError(f"Encabezado CSV inválido: {exc}") from exc
    if not fields or len(fields) != len(set(fields)):
        raise ValueError("El CSV necesita un encabezado sin columnas duplicadas.")
    if not required <= set(fields) or set(fields) - required - (optional or set()):
        raise ValueError("Columnas esperadas: " + ", ".join(sorted(required)) +
                         ". Opcionales: " + ", ".join(sorted(optional or set())))
    try:
        rows = list(reader)
    except csv.Error as exc:
        raise ValueError(f"CSV inválido: {exc}") from exc
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("El número de campos no coincide con el encabezado del CSV.")
    return rows


def write_csv(rows, fields) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def graph_csv(graph: Graph) -> str:
    rows = [{"tipo": "nodo", "origen": node} for node in graph.nodes]
    rows += [{"tipo": "arista", "origen": e.source, "destino": e.target,
              "peso": e.weight, "capacidad": e.capacity} for e in graph.edges]
    return write_csv(rows, ["tipo", "origen", "destino", "peso", "capacidad"])


def project_csv(project: Project, *, pert: bool) -> str:
    rows = []
    for a in project.activities:
        row = {"actividad": a.id, "predecesoras": ";".join(a.predecessors)}
        if pert:
            row.update(optimista=a.optimistic, probable=a.most_likely, pesimista=a.pessimistic)
        else:
            row["duracion"] = a.duration
        rows.append(row)
    return write_csv(rows, list(rows[0]))
