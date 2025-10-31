from __future__ import annotations

from typing import Optional, Tuple


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


def _pattern_summary(pattern: Optional[str]) -> Tuple[str, str]:
    key = (pattern or "").strip().lower()
    if key in {"constraint-ledger", "ledger", "constraint_ledger"}:
        change = (
            "Keep a Constraint Ledger (include/avoid/not-too/vibes), echo after each capture, and confirm before mixing"
        )
        benefit = "prevents contradictions and preserves user intent"
    elif key in {"contrastive-clarify", "contrastive", "clarify"}:
        change = (
            "Use a single contrastive clarifier for ambiguous terms, reflect the choice, then proceed"
        )
        benefit = "reduces guessing and keeps momentum"
    elif key in {"exemplar-propose", "exemplar", "propose"}:
        change = (
            "Offer two tiny exemplars that fit constraints; ask which is closer or what to tweak"
        )
        benefit = "anchors vague requests without long back-and-forth"
    elif key in {"override-hook", "override", "hook"}:
        change = (
            "Add simple staff commands (override/lock/reduce/reset) that apply immediately and are echoed"
        )
        benefit = "enables fast corrections without restarting the flow"
    else:
        change = (
            "Introduce lightweight rules: keep constraints, ask only to resolve gaps, and confirm before acting"
        )
        benefit = "turns ambiguous input into reliable actions"
    return change, benefit


def build_plan_text(
    seed: str,
    friction: str,
    *,
    pattern: Optional[str] = None,
    ascii_only: bool = False,
) -> str:
    change, benefit = _pattern_summary(pattern)

    context = (
        f"Seed: {seed}\n"
        f"Observed issue: {friction}"
    )
    objective = (
        "Guide the assistant to interpret natural speech reliably and reach a confirmed outcome without repetition."
    )

    flow = (
        "1. Problem statement: The assistant sounds friendly but misreads intent from vague wording.\n"
        "2. First draft: Naive paraphrasing leads to random mixes and drift.\n"
        "3. Test: Users repeat themselves; staff cannot correct quickly.\n"
        f"4. Diagnosis: Missing guardrails to retain constraints and disambiguate terms.\n"
        f"5. Reasoning change: {change}.\n"
        "6. Validation: Trials show fewer repeats and clearer proposals with a short recap.\n"
        f"7. Final insight: This approach {benefit}."
    )

    reasoning = (
        "1. Baseline: Vague adjectives caused mismatches and confusion.\n"
        "2. Observation: Repetition and drift signaled missing constraints.\n"
        f"3. Adjustment: {change}.\n"
        f"4. Rationale: Because {friction}, this keeps the conversation aligned.\n"
        "5. Test Result: Short recap + confirmation reduced errors in trials.\n"
        f"6. Insight: Simple rules -> better matches and faster closes."
    )

    output = (
        "Clear recap of constraints, one concise clarifier if needed, two fitting options or direct next step, and a confirmation before finalizing."
    )

    template = (
        "Context\n"
        "-------\n"
        f"{context}\n\n"
        "Objective\n"
        "---------\n"
        f"{objective}\n\n"
        "Flow\n"
        "----\n"
        f"{flow}\n\n"
        "Reasoning Path\n"
        "--------------\n"
        f"{reasoning}\n\n"
        "Output\n"
        "------\n"
        f"{output}\n"
    )

    return _ascii(template, ascii_only).strip() + "\n"

