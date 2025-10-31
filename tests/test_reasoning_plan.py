import pytest

from promptflow_tool.models import IterationStep, SeedQuestion
from promptflow_tool.reasoning_plan import build_plan, format_reasoning_trace


@pytest.fixture
def sample_seed() -> SeedQuestion:
    return SeedQuestion(
        question="How can we improve onboarding?",
        context="A SaaS product wants to increase activation.",
        objective="Map an experimentation path to improve activation.",
        expected_output="Summarised Felix-style plan.",
    )


@pytest.fixture
def sample_steps() -> list[IterationStep]:
    return [
        IterationStep(
            trigger="Support tickets highlighting confusion.",
            change="Clarified welcome messaging.",
            rationale="Reduce friction by explaining value upfront.",
            outcome="Activation rate improved by 5%.",
        ),
        IterationStep(
            trigger="Users still missed key feature.",
            change="Introduced interactive tour.",
            rationale="Guide users through the critical feature.",
            outcome="Feature adoption grew by 12%.",
        ),
    ]


def test_build_plan_includes_all_sections(sample_seed: SeedQuestion, sample_steps: list[IterationStep]):
    plan = build_plan(sample_seed, sample_steps)

    for heading in ["Context", "Objective", "Flow", "Reasoning Path", "Output"]:
        assert heading in plan

    assert (
        "1. Problem statement: Because Support tickets highlighting confusion, we Clarified welcome messaging"
        in plan
    )
    assert "Result: Activation rate improved by 5%." in plan


def test_causal_link_formatting(sample_steps: list[IterationStep]):
    reasoning = format_reasoning_trace(sample_steps)
    assert reasoning.count("\n") == 5
    assert reasoning.startswith("1. Baseline:")
    assert reasoning.endswith("Clarified welcome messaging → Activation rate improved by 5%")
    assert ".," not in reasoning


def test_reasoning_trace_has_six_lines(sample_steps: list[IterationStep]):
    reasoning = format_reasoning_trace(sample_steps)
    lines = [line for line in reasoning.splitlines() if line.strip()]
    assert len(lines) == 6
    assert lines[0].startswith("1. Baseline:")
    assert lines[-1].startswith("6. Insight:")
