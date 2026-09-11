from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from numbers import Real
from typing import Any


@dataclass(frozen=True)
class ValidationError(Exception):
    problems: tuple[str, ...]

    def __str__(self) -> str:
        return "Invalid experiment document: " + "; ".join(self.problems)


def _get(document: dict[str, Any], path: str) -> Any:
    current: Any = document
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def validate_experiment(document: dict[str, Any]) -> None:
    """Validate the minimum evidence needed for a reviewable experiment claim."""
    problems: list[str] = []
    for path in ("run.name", "run.timestamp", "dataset.name", "dataset.split", "model.name", "seed", "metrics"):
        value = _get(document, path)
        if value in (None, "", {}, []):
            problems.append(f"missing '{path}'")
    timestamp = _get(document, "run.timestamp")
    if isinstance(timestamp, str):
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            problems.append("'run.timestamp' must be ISO-8601")
    metrics = _get(document, "metrics")
    if isinstance(metrics, dict):
        invalid = [name for name, value in metrics.items() if not isinstance(value, Real) or isinstance(value, bool)]
        if invalid:
            problems.append("metrics must be numeric: " + ", ".join(sorted(invalid)))
    claims = document.get("claims", [])
    if not isinstance(claims, list):
        problems.append("'claims' must be a list")
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or not claim["text"].strip():
                problems.append(f"claim {index} needs non-empty text")
                continue
            evidence = claim.get("evidence")
            if not isinstance(evidence, list) or not all(isinstance(item, str) and item.strip() for item in evidence):
                problems.append(f"claim {index} needs a non-empty evidence list")
            if claim.get("scope") not in {"synthetic", "benchmark", "production", "unknown"}:
                problems.append(f"claim {index} needs an explicit scope")
    if problems:
        raise ValidationError(tuple(problems))


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- Not provided"


def render_card(document: dict[str, Any]) -> str:
    """Render a validated experiment document as transparent Markdown."""
    validate_experiment(document)
    run = document["run"]
    dataset = document["dataset"]
    model = document["model"]
    metrics = document["metrics"]
    artifacts = document.get("artifacts", {})
    claims = document.get("claims", [])
    limitations = document.get("limitations", [])

    metric_rows = "\n".join(f"| {name} | {value:.6g} |" for name, value in sorted(metrics.items()))
    claim_rows = "\n".join(
        f"- **{claim['scope']}** — {claim['text']}  \n  Evidence: {', '.join(claim['evidence'])}"
        for claim in claims
    ) or "- No performance claims were supplied."
    artifact_rows = "\n".join(f"- **{name}**: {value}" for name, value in sorted(artifacts.items())) or "- Not provided"

    return f"""# Experiment Card: {run['name']}

## Identity

- **Timestamp:** {run['timestamp']}
- **Seed:** {document['seed']}
- **Code revision:** {run.get('revision', 'Not provided')}

## Data and split

- **Dataset:** {dataset['name']}
- **Version:** {dataset.get('version', 'Not provided')}
- **Split:** {dataset['split']}
- **Provenance:** {dataset.get('provenance', 'Not provided')}

## Model

- **Model:** {model['name']}
- **Configuration:** {model.get('configuration', 'Not provided')}

## Metrics

| Metric | Value |
|---|---:|
{metric_rows}

## Claims and evidence

{claim_rows}

## Artifacts

{artifact_rows}

## Limitations

{_bullets([str(item) for item in limitations])}

## Evidence boundary

This card reports the supplied experiment record. It does not independently reproduce results or establish external validity. Claims must retain their declared scope.
"""
