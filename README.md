# Experiment Card

Generate review-ready Markdown cards from structured ML experiment results. The tool makes missing evidence visible instead of turning an unqualified metric into a vague performance claim.

## Install

```bash
python -m pip install git+https://github.com/Jdawgboo/experiment-card.git
```

## Use

```bash
experiment-card examples/experiment.json --output EXPERIMENT_CARD.md
```

The input has explicit fields for the run, dataset, split, model, seed, numeric metrics, artifacts, claims, and limitations. Example input is available in [`examples/experiment.json`](examples/experiment.json).

## What is validated

- run name and ISO-8601 timestamp
- dataset name and split description
- model name and seed
- numeric metrics
- every claim's text, scope, and list of evidence references

## Why the scope field matters

A metric from a synthetic smoke test is not benchmark evidence; a benchmark result is not production evidence. Every claim must declare one of these scopes:

- `synthetic`
- `benchmark`
- `production`
- `unknown`

The rendered card preserves that boundary in its claims-and-evidence section.

## Library usage

```python
from experiment_card import render_card

markdown = render_card(experiment_document)
```

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Licensed under [MIT](LICENSE).
