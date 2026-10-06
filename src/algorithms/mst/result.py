"""Resultados inmutables para algoritmos de árbol de expansión mínima."""

from dataclasses import dataclass

from src.core import Edge
from src.core.edge import Number


@dataclass(frozen=True)
class MSTStep:
    iteration: int
    edge: Edge
    accepted: bool
    reason: str
    accumulated_weight: Number
    components: int


@dataclass(frozen=True)
class MSTResult:
    algorithm: str
    nodes: tuple[str, ...]
    selected_edges: tuple[Edge, ...]
    total_weight: Number
    steps: tuple[MSTStep, ...]
