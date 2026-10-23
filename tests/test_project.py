"""Planificación, múltiples rutas y ejemplo bibliográfico General Foundry."""

import unittest

from src.core.activity import Activity, Project
from src.algorithms.project import CPMAlgorithm, PERTAlgorithm


class ProjectTests(unittest.TestCase):
    def test_cpm_parallel_ends_slack_and_trace(self):
        project = Project((Activity("C", ("A", "B"), duration=4),
                           Activity("A", duration=2), Activity("B", duration=3),
                           Activity("D", duration=1)))
        result = CPMAlgorithm().solve(project)
        self.assertEqual(result.duration, 7)
        self.assertEqual(result.critical_path, ("B", "C"))
        rows = {t.id: t for t in result.timings}
        self.assertEqual(rows["A"].slack, 1)
        self.assertEqual(rows["D"].slack, 6)
        self.assertEqual(rows["C"].early_start, 3)
        self.assertEqual(len(result.steps), 8)

    def test_pert_general_foundry(self):
        data = [("A", (), 1, 2, 3), ("B", (), 2, 3, 4), ("C", ("A",), 1, 2, 3),
                ("D", ("B",), 2, 4, 6), ("E", ("C",), 1, 4, 7),
                ("F", ("C",), 1, 2, 9), ("G", ("D", "E"), 3, 4, 11),
                ("H", ("F", "G"), 1, 2, 3)]
        project = Project(tuple(Activity(n, p, optimistic=a, most_likely=m, pessimistic=b)
                                for n, p, a, m, b in data))
        result = PERTAlgorithm().solve(project, deadline=16)
        self.assertAlmostEqual(result.schedule.duration, 15)
        self.assertEqual(result.schedule.critical_path, ("A", "C", "E", "G", "H"))
        self.assertAlmostEqual(result.critical_path_variance, 112 / 36)
        self.assertAlmostEqual(result.completion_probability, 0.715, delta=0.003)

    def test_multiple_critical_paths_zero_times_and_deterministic_pert(self):
        project = Project((Activity("A", duration=2), Activity("B", duration=2),
                           Activity("C", ("A", "B"), duration=0)))
        result = CPMAlgorithm().solve(project)
        self.assertEqual(result.critical_path_count, 2)
        self.assertEqual(set(result.critical_activities), {"A", "B", "C"})
        pert = Project(tuple(Activity(a.id, a.predecessors, optimistic=a.duration,
                                     most_likely=a.duration, pessimistic=a.duration)
                             for a in project.activities))
        self.assertIsNone(PERTAlgorithm().solve(pert, deadline=3).completion_probability)
        single = Project((Activity("Z", optimistic=0, most_likely=0, pessimistic=0),))
        self.assertEqual(PERTAlgorithm().solve(single, deadline=0).completion_probability, 1)

    def test_invalid_precedence_estimates_and_cycles(self):
        with self.assertRaisesRegex(ValueError, "inexistentes"):
            Project((Activity("A", ("X",), duration=1),))
        with self.assertRaisesRegex(ValueError, "ciclo"):
            CPMAlgorithm().solve(Project((Activity("A", ("B",), duration=1),
                                          Activity("B", ("A",), duration=1))))
        for kwargs in [{"duration": -1}, {"optimistic": 5, "most_likely": 2, "pessimistic": 8},
                       {"duration": 1, "optimistic": 0}]:
            with self.assertRaises(ValueError):
                Activity("A", **kwargs)
