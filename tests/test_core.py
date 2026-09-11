import unittest

from experiment_card import ValidationError, render_card


class ExperimentCardTests(unittest.TestCase):
    def document(self):
        return {
            "run": {"name": "demo", "timestamp": "2026-01-01T00:00:00Z"},
            "dataset": {"name": "fixture", "split": "subject-level"},
            "model": {"name": "linear"},
            "seed": 1,
            "metrics": {"accuracy": 0.9},
            "claims": [{"text": "Smoke test completed.", "scope": "synthetic", "evidence": ["metrics.accuracy"]}],
        }

    def test_renders_evidence_boundary(self) -> None:
        card = render_card(self.document())
        self.assertIn("# Experiment Card: demo", card)
        self.assertIn("Smoke test completed.", card)
        self.assertIn("does not independently reproduce", card)

    def test_rejects_claim_without_evidence(self) -> None:
        document = self.document()
        document["claims"][0].pop("evidence")
        with self.assertRaises(ValidationError):
            render_card(document)

    def test_rejects_non_numeric_metric(self) -> None:
        document = self.document()
        document["metrics"] = {"accuracy": "high"}
        with self.assertRaises(ValidationError):
            render_card(document)


if __name__ == "__main__":
    unittest.main()
