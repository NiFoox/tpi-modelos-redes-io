"""Grafo simple con colección de aristas y adyacencia indexada."""

from .edge import Edge, Number, validate_node_id


class Graph:
    """Mantiene sincronizadas las conexiones y las listas de vecinos.

    Los diccionarios preservan el orden de carga. Las consultas devuelven tuplas
    para que quien las recibe no pueda modificar el estado interno por accidente.
    En grafos dirigidos, neighbors devuelve solamente conexiones salientes.
    """

    def __init__(self, *, directed: bool = False) -> None:
        if not isinstance(directed, bool):
            raise TypeError("directed debe ser un booleano.")
        self._directed = directed
        self._edges: dict[tuple[str, str], Edge] = {}
        self._adjacency: dict[str, dict[str, Edge]] = {}

    @property
    def directed(self) -> bool:
        return self._directed

    @property
    def nodes(self) -> tuple[str, ...]:
        return tuple(self._adjacency)

    @property
    def edges(self) -> tuple[Edge, ...]:
        """Una entrada por conexión, incluso en grafos no dirigidos."""
        return tuple(self._edges.values())

    def _key(self, source: str, target: str) -> tuple[str, str]:
        if not self.directed and target < source:
            return target, source
        return source, target

    def add_node(self, node_id: str) -> None:
        """Agrega un nodo aislado; repetir un identificador no duplica el nodo."""
        validate_node_id(node_id)
        self._adjacency.setdefault(node_id, {})

    def add_edge(
        self,
        source: str,
        target: str,
        *,
        weight: Number | None = None,
        capacity: Number | None = None,
    ) -> Edge:
        """Valida antes de mutar y crea automáticamente los extremos faltantes."""
        edge = Edge(source, target, weight, capacity)
        key = self._key(source, target)
        if key in self._edges:
            raise ValueError("Ya existe una conexión entre esos nodos con esa orientación.")
        self.add_node(source)
        self.add_node(target)
        self._edges[key] = edge
        self._adjacency[source][target] = edge
        if not self.directed:
            self._adjacency[target][source] = edge
        return edge

    def neighbors(self, node_id: str) -> tuple[tuple[str, Edge], ...]:
        """Devuelve pares (vecino, arista); no reorienta la arista almacenada."""
        validate_node_id(node_id)
        if node_id not in self._adjacency:
            raise ValueError(f"No existe el nodo {node_id!r}.")
        return tuple(self._adjacency[node_id].items())

    def remove_edge(self, source: str, target: str) -> Edge:
        """Elimina la conexión y conserva sus extremos, aunque queden aislados."""
        validate_node_id(source)
        validate_node_id(target)
        key = self._key(source, target)
        if key not in self._edges:
            raise ValueError("No existe la conexión indicada.")
        edge = self._edges.pop(key)
        del self._adjacency[edge.source][edge.target]
        if not self.directed:
            del self._adjacency[edge.target][edge.source]
        return edge

    def remove_node(self, node_id: str) -> None:
        """Elimina el nodo y todas sus conexiones entrantes y salientes."""
        validate_node_id(node_id)
        if node_id not in self._adjacency:
            raise ValueError(f"No existe el nodo {node_id!r}.")
        incident = [
            edge for edge in self._edges.values()
            if node_id in (edge.source, edge.target)
        ]
        for edge in incident:
            self.remove_edge(edge.source, edge.target)
        del self._adjacency[node_id]
