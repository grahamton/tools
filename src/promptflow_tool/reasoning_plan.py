"""Construction helpers for PromptFlow reasoning plans."""
from __future__ import annotations

from typing import Iterable, List

from .models import IterationStep, SeedQuestion


TEMPLATE = (
    "Context\n"
    "-------\n"
    "{context}\n\n"
    "Objective\n"
    "---------\n"
    "{objective}\n\n"
    "Flow\n"
    "----\n"
    "{flow}\n\n"
    "Reasoning Path\n"
    "--------------\n"
    "{reasoning}\n\n"
    "Output\n"
    "------\n"
    "{output}\n"
)


def _default(value: str | None, fallback: str) -> str:
    return value.strip() if value and value.strip() else fallback


def _format_flow(steps: Iterable[IterationStep]) -> str:
    lines: List[str] = []
    for index, step in enumerate(steps, start=1):
        lines.append(f"{index}. {step.change} (triggered by {step.trigger})")
    return "\n".join(lines) if lines else "No iterations recorded."


def format_reasoning_trace(steps: Iterable[IterationStep]) -> str:
    """Render a Felix-style reasoning trace emphasising causal links."""

    lines: List[str] = []
    for index, step in enumerate(steps, start=1):
        lines.append(f"Step {index}: Trigger — {step.trigger}")
        lines.append(f"          Change — {step.change}")
        lines.append(
            "          Rationale — {rationale} → Outcome — {outcome}".format(
                rationale=step.rationale, outcome=step.outcome
            )
        )
    return "\n".join(lines) if lines else "No reasoning steps provided."


def build_plan(seed_question: SeedQuestion, steps: Iterable[IterationStep]) -> str:
    """Build the reasoning plan document following the Felix template."""

    steps_list = list(steps)
    context = _default(seed_question.context, seed_question.question)
    objective = _default(seed_question.objective, seed_question.question)
    flow = _format_flow(steps_list)
    reasoning = format_reasoning_trace(steps_list)
    output = _default(
        seed_question.expected_output,
        steps_list[-1].outcome if steps_list else "Outcome pending.",
    )

    return TEMPLATE.format(
        context=context,
        objective=objective,
        flow=flow,
        reasoning=reasoning,
        output=output,
    ).strip() + "\n"
