"""Orden topológico y recorridos hacia adelante y hacia atrás."""

from collections import deque
from dataclasses import dataclass
from math import isclose, isfinite

from src.core.activity import Project
from src.core.edge import Number


@dataclass(frozen=True)
class ActivityTiming:
    id: str
    duration: Number
    early_start: Number
    early_finish: Number
    late_start: Number
    late_finish: Number
    slack: Number
    critical: bool


@dataclass(frozen=True)
class ProjectStep:
    phase: str
    activity: str
    start: Number
    finish: Number


@dataclass(frozen=True)
class ProjectResult:
    duration: Number
    timings: tuple[ActivityTiming, ...]
    critical_activities: tuple[str, ...]
    critical_edges: tuple[tuple[str, str], ...]
    critical_path: tuple[str, ...]
    critical_path_count: int
    steps: tuple[ProjectStep, ...]


def _finite(value: Number) -> Number:
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Los tiempos calculados exceden el rango numérico admitido.")
    return value


def _equal(a: Number, b: Number, scale: Number) -> bool:
    # Escala del proyecto para absorber el error de la pasada hacia atrás en t=0.
    return a == b or isclose(a, b, rel_tol=1e-12, abs_tol=abs(scale) * 1e-12)


def schedule(project: Project, durations: dict[str, Number]) -> ProjectResult:
    activities = {a.id: a for a in project.activities}
    successors: dict[str, list[str]] = {a: [] for a in activities}
    indegree = {a.id: len(a.predecessors) for a in project.activities}
    for activity in project.activities:
        for predecessor in activity.predecessors:
            successors[predecessor].append(activity.id)
    queue = deque(n for n in activities if indegree[n] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for successor in successors[node]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
    if len(order) != len(activities):
        raise ValueError("Las precedencias contienen un ciclo; el proyecto debe ser acíclico.")

    es, ef, ls, lf = {}, {}, {}, {}
    steps = []
    try:
        for node in order:
            es[node] = max((ef[p] for p in activities[node].predecessors), default=0)
            ef[node] = _finite(es[node] + durations[node])
            steps.append(ProjectStep("Adelante", node, es[node], ef[node]))
        duration = max(ef.values())
        for node in reversed(order):
            lf[node] = min((ls[s] for s in successors[node]), default=duration)
            ls[node] = _finite(lf[node] - durations[node])
            steps.append(ProjectStep("Atrás", node, ls[node], lf[node]))
    except OverflowError as exc:
        raise ValueError("Los tiempos calculados exceden el rango numérico admitido.") from exc

    critical = {n for n in order if _equal(ls[n], es[n], duration)}
    critical_edges = tuple(
        (p, n) for n in order for p in activities[n].predecessors
        if p in critical and n in critical and _equal(ef[p], es[n], duration)
    )
    critical_predecessors = {n: [] for n in order}
    for p, n in critical_edges:
        critical_predecessors[n].append(p)
    # Cuenta caminos sin enumerarlos: puede haber una cantidad exponencial.
    counts: dict[str, int] = {}
    chosen_parent = {}
    for n in order:
        if n not in critical:
            counts[n] = 0
        elif not activities[n].predecessors:
            counts[n] = 1
        else:
            preds = [p for p in critical_predecessors[n] if counts[p]]
            counts[n] = sum(counts[p] for p in preds)
            if preds:
                chosen_parent[n] = preds[0]
    ends = [n for n in order if not successors[n] and counts[n] and _equal(ef[n], duration, duration)]
    node = ends[0]
    path = [node]
    while node in chosen_parent:
        node = chosen_parent[node]
        path.append(node)
    timings = tuple(ActivityTiming(
        n, durations[n], es[n], ef[n], ls[n], lf[n],
        0 if n in critical else ls[n] - es[n], n in critical,
    ) for n in order)
    return ProjectResult(
        duration, timings, tuple(n for n in order if n in critical), critical_edges,
        tuple(reversed(path)), sum(counts[n] for n in ends), tuple(steps),
    )


class CPMAlgorithm:
    def solve(self, project: Project) -> ProjectResult:
        if any(a.duration is None for a in project.activities):
            raise ValueError("CPM requiere una duración determinada para cada actividad.")
        return schedule(project, {a.id: a.duration for a in project.activities})
