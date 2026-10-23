"""PERT con tiempos esperados y aproximación normal para una ruta crítica."""

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist

from src.core.activity import Project
from src.core.edge import Number, _validate_number

from .cpm import ProjectResult, _finite, schedule


@dataclass(frozen=True)
class PERTResult:
    schedule: ProjectResult
    variances: tuple[tuple[str, float], ...]
    critical_path_variance: float
    deadline: Number | None
    completion_probability: float | None


class PERTAlgorithm:
    def solve(self, project: Project, *, deadline: Number | None = None) -> PERTResult:
        if deadline is not None:
            _validate_number(deadline, "El plazo")
            if deadline < 0:
                raise ValueError("El plazo no puede ser negativo.")
        durations, variances = {}, {}
        for activity in project.activities:
            if activity.duration is not None:
                raise ValueError("PERT requiere tres estimaciones para cada actividad.")
            a, m, b = activity.optimistic, activity.most_likely, activity.pessimistic
            try:
                durations[activity.id] = _finite(a / 6 + (m / 3) * 2 + b / 6)
                variances[activity.id] = _finite(((b - a) / 6) ** 2)
            except OverflowError as exc:
                raise ValueError("Las estimaciones exceden el rango numérico admitido.") from exc
        result = schedule(project, durations)
        variance = _finite(sum(variances[n] for n in result.critical_path))
        probability = None
        if deadline is not None and result.critical_path_count == 1:
            if variance == 0:
                probability = float(deadline >= result.duration)
            else:
                z = (deadline - result.duration) / sqrt(variance)
                probability = NormalDist().cdf(z)
        return PERTResult(result, tuple(variances.items()), variance, deadline, probability)
