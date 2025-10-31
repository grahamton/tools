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

STAGE_LABELS: List[str] = [
    "Problem statement",
    "First draft",
    "Test",
    "Diagnosis",
    "Reasoning change",
    "Validation",
    "Final insight",
]


def _default(value: str | None, fallback: str) -> str:
    return value.strip() if value and value.strip() else fallback


def _trim_terminal_period(text: str) -> str:
    if not text:
        return text
    stripped = text.rstrip()
    if stripped.endswith((".", "!", "?")):
        stripped = stripped[:-1]
    return stripped


def _format_flow(steps: Iterable[IterationStep]) -> str:
    lines: List[str] = []
    for index, step in enumerate(steps, start=1):
        stage = STAGE_LABELS[index - 1] if index <= len(STAGE_LABELS) else "Additional insight"
        because_clause = (
            f"Because {_trim_terminal_period(step.trigger)}, we {_trim_terminal_period(step.change)}"
        )
        if step.rationale:
            because_clause += f" to {_trim_terminal_period(step.rationale)}"
        sentence = (
            f"{index}. {stage}: {because_clause}. Result: {_trim_terminal_period(step.outcome)}."
        )
        lines.append(sentence)
    return "\n".join(lines) if lines else "No iterations recorded."


def format_reasoning_trace(steps: Iterable[IterationStep]) -> str:
    """Render a Felix-style reasoning trace emphasising causal links."""

    steps_list = list(steps)
    if not steps_list:
        return "No reasoning steps provided."

    first = steps_list[0]
    lines = [
        f"1. Baseline: {first.trigger}",
        f"2. Observation: The issue surfaced as {first.trigger}",
        f"3. Adjustment: {first.change}",
        f"4. Rationale: Because {_trim_terminal_period(first.rationale)}, the fix stays aligned with the goal.",
        f"5. Test Result: {first.outcome}",
        (
            "6. Insight: {change} → {outcome}".format(
                change=_trim_terminal_period(first.change),
                outcome=_trim_terminal_period(first.outcome),
            )
        ),
    ]
    return "\n".join(lines)


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
