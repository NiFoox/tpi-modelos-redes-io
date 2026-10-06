"""Conexiones con peso, capacidad o ambos valores."""

from dataclasses import dataclass
from math import isfinite

Number = int | float


def validate_node_id(node_id: str) -> None:
    """Evita identificar accidentalmente 'A' y ' A ' como nodos distintos."""
    if not isinstance(node_id, str):
        raise TypeError("El identificador del nodo debe ser texto.")
    if not node_id or node_id != node_id.strip():
        raise ValueError("El nodo debe tener un identificador sin espacios en los extremos.")


def _validate_number(value: Number, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} debe ser un número real (int o float).")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} debe ser finito.")


@dataclass(frozen=True)
class Edge:
    """Arista inmutable; la orientación la determina el Graph contenedor.

    None significa dato no proporcionado. Cero es un valor válido.
    El modelo admite pesos negativos; cada algoritmo impone sus restricciones.
    """

    source: str
    target: str
    weight: Number | None = None
    capacity: Number | None = None

    def __post_init__(self) -> None:
        validate_node_id(self.source)
        validate_node_id(self.target)
        if self.source == self.target:
            raise ValueError("Esta versión no admite bucles: origen y destino deben diferir.")
        if self.weight is None and self.capacity is None:
            raise ValueError("La conexión debe tener un peso o una capacidad.")
        if self.weight is not None:
            _validate_number(self.weight, "El peso")
        if self.capacity is not None:
            _validate_number(self.capacity, "La capacidad")
            if self.capacity < 0:
                raise ValueError("La capacidad no puede ser negativa.")
