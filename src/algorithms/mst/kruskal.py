"""Kruskal con conjuntos disjuntos y registro de decisiones."""

from math import isfinite

from src.core import Graph
from src.core.edge import Number

from .result import MSTResult, MSTStep


class _DisjointSet:
    def __init__(self, nodes: tuple[str, ...]) -> None:
        self.parent = {node: node for node in nodes}
        self.size = {node: 1 for node in nodes}
        self.components = len(nodes)

    def find(self, node: str) -> str:
        # Compresión de caminos por mitades, sin recursión.
        while node != self.parent[node]:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def union(self, source: str, target: str) -> bool:
        first, second = self.find(source), self.find(target)
        if first == second:
            return False
        if self.size[first] < self.size[second]:
            first, second = second, first
        self.parent[second] = first
        self.size[first] += self.size[second]
        self.components -= 1
        return True


class KruskalAlgorithm:
    def solve(self, graph: Graph) -> MSTResult:
        """Obtiene un MST sin modificar graph; rechaza redes sin árbol abarcador."""
        if graph.directed:
            raise ValueError("Kruskal requiere un grafo no dirigido.")
        nodes, edges = graph.nodes, graph.edges
        if not nodes:
            raise ValueError("El grafo debe contener al menos un nodo.")
        if any(edge.weight is None for edge in edges):
            raise ValueError("Todas las conexiones deben tener un peso para Kruskal.")

        # Los extremos canónicos resuelven empates sin depender del orden de carga.
        ordered = sorted(edges, key=lambda e: (
            e.weight, min(e.source, e.target), max(e.source, e.target)
        ))
        groups = _DisjointSet(nodes)
        selected = []
        steps = []
        total: Number = 0
        for iteration, edge in enumerate(ordered, start=1):
            accepted = groups.union(edge.source, edge.target)
            if accepted:
                assert edge.weight is not None  # Validado antes de ordenar.
                try:
                    total += edge.weight
                except OverflowError as exc:
                    raise ValueError("El costo total excede el rango numérico admitido.") from exc
                if isinstance(total, float) and not isfinite(total):
                    raise ValueError("El costo total excede el rango numérico admitido.")
                selected.append(edge)
            steps.append(MSTStep(
                iteration, edge, accepted,
                "Une componentes distintas" if accepted else "Formaría un ciclo",
                total, groups.components,
            ))
            if len(selected) == len(nodes) - 1:
                break

        if groups.components != 1:
            raise ValueError(
                "El grafo está desconectado: no existe un árbol de expansión "
                f"que conecte todos los nodos ({groups.components} componentes)."
            )
        return MSTResult("Kruskal", nodes, tuple(selected), total, tuple(steps))
