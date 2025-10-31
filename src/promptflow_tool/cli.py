"""Typer CLI for building PromptFlow reasoning plans."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Tuple

import typer
import yaml

from .models import IterationStep, SeedQuestion
from .reasoning_plan import build_plan

app = typer.Typer(help="PromptFlow tooling for reasoning plans.")


def _load_description(path: Path) -> Tuple[SeedQuestion, Iterable[IterationStep]]:
    content = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)

    seed = SeedQuestion.parse_obj(data["seed_question"])
    steps = [IterationStep.parse_obj(step) for step in data.get("steps", [])]
    return seed, steps


@app.command()
def plan(description: Path = typer.Argument(..., help="Path to a plan description")) -> None:
    """Generate a Felix-style reasoning plan from structured input."""

    seed, steps = _load_description(description)
    document = build_plan(seed, steps)
    typer.echo(document)


def main() -> None:  # pragma: no cover - entry point for scripts
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
