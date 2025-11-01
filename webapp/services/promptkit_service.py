from __future__ import annotations

from typing import Any, Dict, Optional

from promptkit.cards import make_iterate_card
from promptkit.plan import build_plan_text
from promptkit.ticket import build_ticket_text


def run_promptkit(
    mode: str,
    seed: str,
    friction: str,
    pattern: Optional[str] = None,
    ascii_only: bool = False,
    json_out: bool = False,
) -> Dict[str, Any]:
    """Run PromptKit for the requested mode and return text/optional JSON.

    Returns a dict with keys:
    - text: str
    - json: Optional[dict]
    - filename_hint: Suggested filename stem
    """
    mode = (mode or "iterate").strip().lower()

    if mode == "iterate":
        card = make_iterate_card(seed, friction, ascii_only=ascii_only, pattern=pattern)
        text = card.render_text()
        payload = None
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
        return {
            "text": text,
            "json": payload,
            "filename_hint": f"iterate_{card.id}" if getattr(card, "id", None) else "iterate_card",
        }

    if mode == "plan":
        text = build_plan_text(seed=seed, friction=friction, pattern=pattern, ascii_only=ascii_only)
        return {"text": text, "json": None, "filename_hint": "plan"}

    if mode == "ticket":
        text = build_ticket_text(
            seed=seed,
            friction=friction,
            client=None,
            prompt_brief=None,
            real_problem=None,
            test_problem=None,
            goal=None,
            success=None,
            ascii_only=ascii_only,
        )
        return {"text": text, "json": None, "filename_hint": "ticket"}

    raise ValueError(f"Unsupported mode: {mode}")

