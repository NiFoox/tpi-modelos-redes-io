"""Prim con cola de prioridad y registro de la expansión del árbol."""

from heapq import heappop, heappush
from math import isfinite

from src.core import Graph
from src.core.edge import Number, validate_node_id

from .result import MSTResult, MSTStep


class PrimAlgorithm:
    def solve(self, graph: Graph, *, start: str | None = None) -> MSTResult:
        """Obtiene un MST desde start; por defecto usa el menor ID lexicográfico."""
        if graph.directed:
            raise ValueError("Prim requiere un grafo no dirigido.")
        nodes, edges = graph.nodes, graph.edges
        if not nodes:
            raise ValueError("El grafo debe contener al menos un nodo.")
        if any(edge.weight is None for edge in edges):
            raise ValueError("Todas las conexiones deben tener un peso para Prim.")
        if start is None:
            start = min(nodes)
        validate_node_id(start)
        if start not in nodes:
            raise ValueError("El nodo inicial no existe en el grafo.")

        visited = {start}
        frontier = []
        selected = []
        steps = []
        total: Number = 0

        def expand(node: str) -> None:
            for neighbor, edge in graph.neighbors(node):
                if neighbor not in visited:
                    heappush(frontier, (
                        edge.weight, min(edge.source, edge.target),
                        max(edge.source, edge.target), neighbor, edge,
                    ))

        expand(start)
        while frontier and len(visited) < len(nodes):
            _, _, _, neighbor, edge = heappop(frontier)
            accepted = neighbor not in visited
            if accepted:
                assert edge.weight is not None
                try:
                    total += edge.weight
                except OverflowError as exc:
                    raise ValueError("El costo total excede el rango numérico admitido.") from exc
                if isinstance(total, float) and not isfinite(total):
                    raise ValueError("El costo total excede el rango numérico admitido.")
                visited.add(neighbor)
                selected.append(edge)
                expand(neighbor)
            steps.append(MSTStep(
                len(steps) + 1, edge, accepted,
                "Incorpora un nodo al árbol" if accepted else "Ambos extremos ya pertenecen al árbol",
                total, len(nodes) - len(selected),
            ))

        if len(visited) != len(nodes):
            raise ValueError(
                "El grafo está desconectado: no existe un árbol de expansión "
                "que conecte todos los nodos."
            )
        return MSTResult("Prim", nodes, tuple(selected), total, tuple(steps))
