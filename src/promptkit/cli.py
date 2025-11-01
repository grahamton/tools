"""Typer CLI for PromptKit diagnostics (MVP)."""
from __future__ import annotations

import json
from typing import Optional

import typer

from .cards import make_iterate_card
from .plan import build_plan_text
from .ticket import build_ticket_text


app = typer.Typer(help="PromptKit: Prompt System Diagnostics Framework — stop guessing; diagnose and standardize fixes.")


@app.command()
def iterate(
    seed: str = typer.Option(..., help="One-line seed (role + goal)"),
    friction: str = typer.Option(..., help="Biggest current friction/failure"),
    pattern: str = typer.Option(None, help="Optional pattern(s): constraint-ledger | contrastive-clarify | exemplar-propose | override-hook | state-bag | slot-filling (comma-separated to combine)"),
    ascii_only: bool = typer.Option(False, "--ascii", help="Emit ASCII-only output"),
    json_out: bool = typer.Option(False, "--json", help="Return machine-readable JSON"),
) -> None:
    """Generate a single iterate card (Diagnosis -> Fix -> Validation)."""

    card = make_iterate_card(seed, friction, ascii_only=ascii_only, pattern=pattern)
    if json_out:
        payload = {
            "id": card.id,
            "seed": card.seed,
            "friction": card.friction,
            "diagnosis": card.diagnosis,
            "fix": {
                "rules": card.fix_rules,
                "prompt_patch": card.prompt_patch,
                "examples": card.examples,
            },
            "validation": {
                "scenarios": card.validation_scenarios,
                "pass_criteria": card.validation_pass,
            },
        }
        typer.echo(json.dumps(payload, ensure_ascii=ascii_only, indent=2))
    else:
        typer.echo(card.render_text())


@app.command()
def plan(
    seed: str = typer.Option(..., help="One-line seed (role + goal)"),
    friction: str = typer.Option(..., help="Observed issue / biggest friction"),
    pattern: str = typer.Option(None, help="Optional pattern to emphasize in plan"),
    ascii_only: bool = typer.Option(False, "--ascii", help="Emit ASCII-only output"),
) -> None:
    """Generate a compact plan (Context, Objective, Flow, Reasoning Path, Output)."""

    text = build_plan_text(seed=seed, friction=friction, pattern=pattern, ascii_only=ascii_only)
    typer.echo(text)


@app.command()
def ticket(
    seed: str = typer.Option(..., help="One-line seed (role + goal)"),
    friction: str = typer.Option(..., help="Observed issue / biggest friction"),
    client: str = typer.Option(None, help="Client name"),
    prompt_brief: str = typer.Option(None, help="One-sentence prompt brief"),
    real_problem: str = typer.Option(None, help="What is failing in production"),
    test_problem: str = typer.Option(None, help="What this validates about PromptKit"),
    goal: str = typer.Option(None, help="What success looks like"),
    success: list[str] = typer.Option(None, "--success", help="Add success criterion (repeatable)"),
    ascii_only: bool = typer.Option(False, "--ascii", help="Emit ASCII-only output"),
) -> None:
    """Print a PromptKit ticket (template filled from args)."""

    text = build_ticket_text(
        seed=seed,
        friction=friction,
        client=client,
        prompt_brief=prompt_brief,
        real_problem=real_problem,
        test_problem=test_problem,
        goal=goal,
        success=success,
        ascii_only=ascii_only,
    )
    typer.echo(text)


def app_main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    app_main()
