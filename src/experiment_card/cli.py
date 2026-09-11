from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .core import ValidationError, render_card


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a validated ML experiment card from JSON.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Write Markdown to this path instead of stdout")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("Top-level JSON value must be an object.")
        card = render_card(document)
    except (OSError, ValueError, json.JSONDecodeError, ValidationError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.write_text(card, encoding="utf-8")
    else:
        print(card, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
