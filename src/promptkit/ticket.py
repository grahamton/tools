from __future__ import annotations

from typing import Iterable, List, Optional


def _ascii(text: str, enabled: bool) -> str:
    if not enabled:
        return text
    return (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
    )


def build_ticket_text(
    *,
    seed: str,
    friction: str,
    client: Optional[str] = None,
    prompt_brief: Optional[str] = None,
    real_problem: Optional[str] = None,
    test_problem: Optional[str] = None,
    goal: Optional[str] = None,
    success: Optional[Iterable[str]] = None,
    ascii_only: bool = False,
) -> str:
    client_line = client or "<client>"
    brief_line = (
        prompt_brief
        or f"Write or refine a conversational objective for: {seed}"
    )
    real_line = real_problem or f"Observed failure: {friction}"
    test_line = (
        test_problem
        or "Validate PromptKit's explain-first fixes address this friction deterministically."
    )
    goal_line = (
        goal
        or "Deliver a human-feeling flow that captures constraints, avoids repetition, and confirms resolution."
    )

    if success:
        success_list: List[str] = list(success)
    else:
        success_list = [
            "Echo captured constraints; never contradict them",
            "Ask only to resolve gaps or conflicts (no repeats)",
            "Provide a recap and explicit confirmation before finalizing",
        ]

    lines: List[str] = []
    lines.append("Client: " + client_line)
    lines.append("Prompt Brief: " + brief_line)
    lines.append("Real Problem: " + real_line)
    lines.append("Test Problem: " + test_line)
    lines.append("Goal: " + goal_line)
    lines.append("Seed: " + seed)
    lines.append("Friction: " + friction)
    lines.append("Success Criteria:")
    for s in success_list:
        lines.append("- " + s)
    text = "\n".join(lines) + "\n"
    return _ascii(text, ascii_only)

