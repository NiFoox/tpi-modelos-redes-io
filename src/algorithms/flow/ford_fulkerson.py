"""Ford-Fulkerson con caminos aumentantes BFS (variante Edmonds-Karp)."""

from collections import deque
from dataclasses import dataclass
from math import isfinite

from src.core import Edge, Graph
from src.core.edge import Number, validate_node_id


@dataclass(frozen=True)
class FlowStep:
    iteration: int
    path: tuple[str, ...]
    directions: tuple[str, ...]
    augmentation: Number
    total_flow: Number


@dataclass(frozen=True)
class EdgeFlow:
    edge: Edge
    flow: Number


@dataclass(frozen=True)
class MaxFlowResult:
    source: str
    sink: str
    total_flow: Number
    edge_flows: tuple[EdgeFlow, ...]
    source_side: tuple[str, ...]
    cut_edges: tuple[Edge, ...]
    cut_capacity: Number
    steps: tuple[FlowStep, ...]


@dataclass
class _ResidualArc:
    target: str
    reverse: int
    remaining: Number
    edge_index: int
    forward: bool


class FordFulkersonAlgorithm:
    def solve(self, graph: Graph, *, source: str, sink: str) -> MaxFlowResult:
        if not graph.directed:
            raise ValueError("Flujo máximo requiere una red dirigida.")
        for node in (source, sink):
            validate_node_id(node)
            if node not in graph.nodes:
                raise ValueError(f"No existe el nodo {node!r}.")
        if source == sink:
            raise ValueError("La fuente y el sumidero deben ser diferentes.")
        edges = graph.edges
        if any(e.capacity is None for e in edges):
            raise ValueError("Todas las conexiones deben tener capacidad.")

        # Cada arista original tiene SU arco inverso, aun si existe otra arista
        # original en sentido opuesto. No se mezclan sus capacidades ni flujos.
        residual: dict[str, list[_ResidualArc]] = {n: [] for n in graph.nodes}
        for i, edge in enumerate(edges):
            assert edge.capacity is not None
            u, v = edge.source, edge.target
            forward = _ResidualArc(v, len(residual[v]), edge.capacity, i, True)
            backward = _ResidualArc(u, len(residual[u]), 0, i, False)
            residual[u].append(forward)
            residual[v].append(backward)

        total: Number = 0
        flows: list[Number] = [0] * len(edges)
        steps = []
        while True:
            parents: dict[str, tuple[str, int]] = {}
            reached = {source}
            queue = deque([source])
            while queue and sink not in reached:
                node = queue.popleft()
                for j, arc in enumerate(residual[node]):
                    if arc.remaining > 0 and arc.target not in reached:
                        reached.add(arc.target)
                        parents[arc.target] = node, j
                        queue.append(arc.target)
                        if arc.target == sink:
                            break
            if sink not in reached:
                break

            path = []
            node = sink
            while node != source:
                previous, j = parents[node]
                path.append((previous, j))
                node = previous
            path.reverse()
            amount = min(residual[u][j].remaining for u, j in path)
            try:
                total += amount
            except OverflowError as exc:
                raise ValueError("El flujo excede el rango numérico admitido.") from exc
            if isinstance(total, float) and not isfinite(total):
                raise ValueError("El flujo excede el rango numérico admitido.")
            directions = []
            for u, j in path:
                arc = residual[u][j]
                arc.remaining -= amount
                residual[arc.target][arc.reverse].remaining += amount
                flows[arc.edge_index] += amount if arc.forward else -amount
                directions.append("Directo" if arc.forward else "Inverso (cancelación)")
            steps.append(FlowStep(
                len(steps) + 1, (source,) + tuple(residual[u][j].target for u, j in path),
                tuple(directions), amount, total,
            ))

        cut = tuple(e for e in edges if e.source in reached and e.target not in reached)
        cut_capacity = sum(e.capacity for e in cut)
        return MaxFlowResult(
            source, sink, total, tuple(EdgeFlow(e, f) for e, f in zip(edges, flows)),
            tuple(n for n in graph.nodes if n in reached), cut, cut_capacity, tuple(steps),
        )
