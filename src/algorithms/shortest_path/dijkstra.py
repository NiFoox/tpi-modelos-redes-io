"""Dijkstra con cola de prioridad y registro de relajaciones."""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf, isfinite

from src.core import Edge, Graph
from src.core.edge import Number, validate_node_id


@dataclass(frozen=True)
class DijkstraStep:
    iteration: int
    source: str
    target: str
    previous_distance: Number
    candidate_distance: Number
    accepted: bool


@dataclass(frozen=True)
class ShortestPathResult:
    source: str
    target: str
    distance: Number
    path: tuple[str, ...]
    selected_edges: tuple[Edge, ...]
    distances: tuple[tuple[str, Number], ...]
    steps: tuple[DijkstraStep, ...]

    @property
    def reachable(self) -> bool:
        return bool(self.path)


class DijkstraAlgorithm:
    def solve(self, graph: Graph, *, source: str, target: str) -> ShortestPathResult:
        """Calcula distancias a todos los nodos y reconstruye la ruta solicitada."""
        for node in (source, target):
            validate_node_id(node)
            if node not in graph.nodes:
                raise ValueError(f"No existe el nodo {node!r}.")
        for edge in graph.edges:
            if edge.weight is None or edge.weight < 0:
                raise ValueError("Dijkstra requiere pesos no negativos en todas las conexiones.")

        distances: dict[str, Number] = dict.fromkeys(graph.nodes, inf)
        distances[source] = 0
        parents: dict[str, tuple[str, Edge]] = {}
        frontier = [(0, source)]
        settled = set()
        steps = []
        while frontier:
            distance, node = heappop(frontier)
            if node in settled:
                continue
            settled.add(node)
            for neighbor, edge in graph.neighbors(node):
                if neighbor in settled:
                    continue
                assert edge.weight is not None
                try:
                    candidate = distance + edge.weight
                except OverflowError as exc:
                    raise ValueError("La distancia excede el rango numérico admitido.") from exc
                if isinstance(candidate, float) and not isfinite(candidate):
                    raise ValueError("La distancia excede el rango numérico admitido.")
                previous = distances[neighbor]
                accepted = candidate < previous
                steps.append(DijkstraStep(
                    len(steps) + 1, node, neighbor, previous, candidate, accepted,
                ))
                if accepted:
                    distances[neighbor] = candidate
                    parents[neighbor] = node, edge
                    heappush(frontier, (candidate, neighbor))

        path, selected = [], []
        if distances[target] != inf:
            node = target
            path.append(node)
            while node != source:
                node, edge = parents[node]
                path.append(node)
                selected.append(edge)
        return ShortestPathResult(
            source, target, distances[target], tuple(reversed(path)),
            tuple(reversed(selected)), tuple(distances.items()), tuple(steps),
        )
