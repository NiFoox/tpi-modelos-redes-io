"""Actividades inmutables para proyectos CPM y PERT."""

from dataclasses import dataclass

from .edge import Number, _validate_number, validate_node_id


@dataclass(frozen=True)
class Activity:
    id: str
    predecessors: tuple[str, ...] = ()
    duration: Number | None = None
    optimistic: Number | None = None
    most_likely: Number | None = None
    pessimistic: Number | None = None

    def __post_init__(self) -> None:
        validate_node_id(self.id)
        if isinstance(self.predecessors, str):
            raise TypeError("Las predecesoras deben ser una colección de identificadores.")
        object.__setattr__(self, "predecessors", tuple(self.predecessors))
        for node in self.predecessors:
            validate_node_id(node)
        if len(set(self.predecessors)) != len(self.predecessors):
            raise ValueError("Una actividad no puede repetir predecesoras.")
        if self.id in self.predecessors:
            raise ValueError("Una actividad no puede precederse a sí misma.")
        estimates = (self.optimistic, self.most_likely, self.pessimistic)
        if self.duration is not None:
            if any(t is not None for t in estimates):
                raise ValueError("Use duración CPM o tres estimaciones PERT, sin mezclarlas.")
            values = (self.duration,)
        else:
            if any(t is None for t in estimates):
                raise ValueError("PERT requiere las tres estimaciones de tiempo.")
            values = estimates
        for value in values:
            _validate_number(value, "El tiempo")
            if value < 0:
                raise ValueError("Los tiempos no pueden ser negativos.")
        if self.duration is None and not self.optimistic <= self.most_likely <= self.pessimistic:
            raise ValueError("PERT requiere optimista <= más probable <= pesimista.")


@dataclass(frozen=True)
class Project:
    activities: tuple[Activity, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "activities", tuple(self.activities))
        if not self.activities:
            raise ValueError("El proyecto debe contener al menos una actividad.")
        if any(not isinstance(a, Activity) for a in self.activities):
            raise TypeError("El proyecto debe contener objetos Activity.")
        ids = [a.id for a in self.activities]
        if len(set(ids)) != len(ids):
            raise ValueError("Hay identificadores de actividad duplicados.")
        known = set(ids)
        for activity in self.activities:
            missing = set(activity.predecessors) - known
            if missing:
                raise ValueError(f"Predecesoras inexistentes en {activity.id}: {', '.join(sorted(missing))}.")
