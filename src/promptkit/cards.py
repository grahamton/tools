from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IterateCard:
    id: str
    seed: str
    friction: str
    diagnosis: List[str]
    fix_rules: List[str]
    prompt_patch: List[str]
    examples: List[str]
    validation_scenarios: List[str]
    validation_pass: List[str]
    model_considerations: List[str] = field(default_factory=list)

    def render_text(self) -> str:
        lines: List[str] = []
        lines.append(f"Iterate Card - {self.id}")
        # Human summary (deterministic): compress fix rules into a terse line
        if self.fix_rules:
            def _strip(s: str) -> str:
                return s.strip().strip('"').rstrip('.')
            summary = "; ".join(_strip(r) for r in self.fix_rules)
            lines.append("- Human summary")
            lines.append(f"  - {summary}.")
        lines.append("- Diagnosis")
        for d in self.diagnosis:
            lines.append(f"  - {d}")
        lines.append("- Fix")
        for r in self.fix_rules:
            lines.append(f"  - {r}")
        lines.append("- Prompt patch (drop-in)")
        for p in self.prompt_patch:
            lines.append(f"  - {p}")
        # Where to place in your prompt (heuristic grouping)
        def _section_for(p: str) -> str:
            low = p.lower()
            if any(k in low for k in ["state bag", "ledger", "state:", "constraint ledger"]):
                return "State/Memory"
            if any(k in low for k in ["override:", "lock:", "reduce:", "reset", "recognize commands", "override"]):
                return "Overrides"
            if any(k in low for k in ["contrast", "clarif", "either/or", "ambiguous"]):
                return "Clarifiers"
            if any(k in low for k in ["offer two options", "option a", "option b", "exemplar"]):
                return "Interaction/Output"
            return "Rules/Policy"
        placement: dict[str, List[str]] = {"Rules/Policy": [], "State/Memory": [], "Clarifiers": [], "Overrides": [], "Interaction/Output": []}
        for p in self.prompt_patch:
            placement[_section_for(p)].append(p)
        lines.append("- Where to place in your prompt")
        for sec in ["Rules/Policy", "State/Memory", "Clarifiers", "Overrides", "Interaction/Output"]:
            if placement[sec]:
                lines.append(f"  - {sec}")
                for p in placement[sec]:
                    lines.append(f"    - {p}")
        if self.examples:
            lines.append("- Example phrasing")
            for e in self.examples:
                lines.append(f"  - {e}")
        lines.append("- Validation")
        lines.append("  - Scenarios")
        for s in self.validation_scenarios:
            lines.append(f"    - {s}")
        lines.append("  - Pass criteria")
        for pc in self.validation_pass:
            lines.append(f"    - {pc}")
        if self.model_considerations:
            lines.append("- Model considerations")
            for mc in self.model_considerations:
                lines.append(f"  - {mc}")
        return "\n".join(lines) + "\n"


def _matches_close_loop(friction: str) -> bool:
    text = friction.lower()
    keywords = [
        "repeat",
        "repeats",
        "repeating",
        "apology",
        "apolog",
        "confirm",
        "resolution",
        "close",
        "loop",
    ]
    return any(k in text for k in keywords)


# ---- Pattern builders (no scoring) ----

def build_constraint_ledger(seed: str, friction: str) -> IterateCard:
    id_ = "Constraint Ledger"
    diagnosis = [
        "Vague adjectives aren't grounded; constraints get lost",
        "No recap before action; easy to contradict user wishes",
    ]
    fix_rules = [
        "Maintain a Constraint Ledger: include, avoid, not-too qualifiers, vibes",
        "Echo constraints after each capture; do not contradict them",
        "Ask only to resolve conflicts or fill missing constraints",
        "Before mixing, recap constraints and confirm",
    ]
    prompt_patch = [
        '"Start a Constraint Ledger: include[], avoid[], not_too[], vibes[]."',
        '"After each user message, echo the ledger succinctly."',
        '"Only ask to resolve conflicts or missing items, not to repeat."',
        '"Before committing, recap ledger and ask: Did I capture this right?"',
    ]
    examples = [
        "Heard: bold vibe, not too spicy, buttery. Ledger: include[buttery], avoid[chili], not_too[spicy], vibes[bold]. Did I capture this right?",
    ]
    validation_scenarios = [
        "'Bold not too spicy' -> ledger avoids heat, keeps richness; confirm",
        "'Sweet but airy' -> ledger keeps light/crisp vibe; propose fitting option",
        "Conflicting term ('spicy' + 'not too spicy') -> ask one clarifier, then lock",
    ]
    validation_pass = [
        "Ledger echoed before action; no contradictions",
        "At most one targeted clarifier for conflicts",
        "Final recap + confirmation present",
    ]
    return IterateCard(
        id=id_,
        seed=seed,
        friction=friction,
        diagnosis=diagnosis,
        fix_rules=fix_rules,
        prompt_patch=prompt_patch,
        examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def build_contrastive_clarify(seed: str, friction: str) -> IterateCard:
    id_ = "Contrastive Clarifier"
    diagnosis = [
        "Ambiguous adjectives branch multiple ways; agent guesses and drifts",
    ]
    fix_rules = [
        "Use a single either/or probe to pin meaning",
        "Reflect the chosen meaning and proceed; avoid stacked probes",
        "Prefer concrete contrasts tied to the domain",
    ]
    prompt_patch = [
        '"When a term is ambiguous, ask one contrast: By bold, do you mean richer or spicier?"',
        '"After answer, reflect: Understood, bold=richer. Moving on."',
        '"Do not chain multiple clarifiers back-to-back."',
    ]
    examples = [
        "By bold, do you mean richer or spicier? -> Got it, richer.",
    ]
    validation_scenarios = [
        "User says 'bold' -> one contrastive probe -> choice reflected",
        "User offers own meaning -> accept and proceed without extra probe",
    ]
    validation_pass = [
        "Exactly one clarifier for an ambiguity",
        "Reflected choice appears before next step",
    ]
    return IterateCard(
        id=id_, seed=seed, friction=friction,
        diagnosis=diagnosis, fix_rules=fix_rules,
        prompt_patch=prompt_patch, examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def build_exemplar_propose(seed: str, friction: str) -> IterateCard:
    id_ = "Exemplar Propose"
    diagnosis = [
        "Free-form replies stay abstract; users struggle to anchor taste",
    ]
    fix_rules = [
        "Propose two tiny exemplars that both fit constraints",
        "Ask which is closer (A or B) or what to tweak",
        "Keep exemplars concrete and minimal (3-4 traits)",
    ]
    prompt_patch = [
        '"Offer two options: Option A: <concrete traits>. Option B: <concrete traits>."',
        '"Ask: Which is closer, A or B? Or what should I tweak?"',
        '"Ensure options respect the current Constraint Ledger."',
    ]
    examples = [
        "A) buttery-salty with hint of chili; B) smoky-rich without heat. Closer to A or B?",
    ]
    validation_scenarios = [
        "With 'not too spicy' in ledger -> both exemplars avoid high heat",
        "User picks A -> recap and confirm before mixing",
    ]
    validation_pass = [
        "Exemplars align with constraints",
        "Choice captured and reflected before action",
    ]
    return IterateCard(
        id=id_, seed=seed, friction=friction,
        diagnosis=diagnosis, fix_rules=fix_rules,
        prompt_patch=prompt_patch, examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def build_override_hook(seed: str, friction: str) -> IterateCard:
    id_ = "Override Hook"
    diagnosis = [
        "Staff lacks quick adjustment commands; fixes require redoing the flow",
    ]
    fix_rules = [
        "Support simple text commands: override, lock, reduce, reset",
        "Honor overrides immediately and reflect the updated state",
        "Keep a visible list of active overrides",
    ]
    prompt_patch = [
        '"Recognize commands: override:<term>, lock:<term>, reduce:<term>, reset."',
        '"Apply and echo: Applied override:no chili. Active overrides:[no chili]."',
        '"Ensure proposals respect overrides and ledger."',
    ]
    examples = [
        "Staff: override: no chili -> Agent: Applied override:no chili. Ledger updated.",
    ]
    validation_scenarios = [
        "After 'no chili' override -> proposals contain zero chili",
        "Lock 'buttery' -> proposals keep buttery trait across tweaks",
    ]
    validation_pass = [
        "Overrides reflected immediately in recap",
        "No contradictions with active overrides",
    ]
    return IterateCard(
        id=id_, seed=seed, friction=friction,
        diagnosis=diagnosis, fix_rules=fix_rules,
        prompt_patch=prompt_patch, examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def build_state_bag(seed: str, friction: str) -> IterateCard:
    id_ = "State Bag"
    diagnosis = [
        "Conversation drifts due to missing explicit state",
        "Contradictions appear because prior constraints aren't echoed",
    ]
    fix_rules = [
        "Maintain a State Bag: goal, include[], avoid[], not_too[], memory[], next_step, confirmed=false",
        "After each user message, update and echo state succinctly",
        "Ask only to resolve missing/conflicting items; otherwise proceed",
        "Before finalizing, recap state and set confirmed=true on explicit yes",
    ]
    prompt_patch = [
        '"Maintain State Bag: goal[], include[], avoid[], not_too[], memory[], next_step, confirmed=false."',
        '"After each user message, update and echo state succinctly."',
        '"Ask only to resolve missing/conflicting items; otherwise proceed."',
        '"Before finalizing, recap state and set confirmed=true on explicit yes."',
    ]
    examples = [
        "State: goal=custom snack; include[buttery]; avoid[chili]; not_too[spicy]; next_step=propose A/B; confirmed=false.",
    ]
    validation_scenarios = [
        "Conflict -> one clarifier -> state updated -> proceed",
        "Before action -> state recap -> explicit confirmation",
    ]
    validation_pass = [
        "No contradictions against echoed state",
        "<=1 clarifier per conflict; explicit confirmation present",
    ]
    return IterateCard(
        id=id_, seed=seed, friction=friction,
        diagnosis=diagnosis, fix_rules=fix_rules,
        prompt_patch=prompt_patch, examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def build_slot_filling(seed: str, friction: str) -> IterateCard:
    id_ = "Slot Filling"
    diagnosis = [
        "Repeated questions caused by missing required fields",
        "Fields gathered piecemeal increase user effort",
    ]
    fix_rules = [
        "Define required slots: entity, intent, include[], avoid[], not_too[], success_check",
        "Ask only for missing slots; never re-ask captured ones",
        "Echo captured slots and confirm before acting",
    ]
    prompt_patch = [
        '"Required slots: entity, intent, include[], avoid[], not_too[], success_check."',
        '"Ask only for missing slots; do not re-ask captured ones."',
        '"Echo captured slots; confirm summary before acting."',
    ]
    examples = [
        "Captured: entity=snack; intent=contrast options; include[buttery]; avoid[chili]; not_too[spicy]. Confirm?",
    ]
    validation_scenarios = [
        "Partial info -> ask only missing -> summary + confirm",
        "Full info -> no extra asks -> proceed",
    ]
    validation_pass = [
        "No redundant asks",
        "Summary + confirmation before action",
    ]
    return IterateCard(
        id=id_, seed=seed, friction=friction,
        diagnosis=diagnosis, fix_rules=fix_rules,
        prompt_patch=prompt_patch, examples=examples,
        validation_scenarios=validation_scenarios,
        validation_pass=validation_pass,
    )


def make_iterate_card(
    seed: str,
    friction: str,
    ascii_only: bool = False,
    pattern: Optional[str] = None,
) -> IterateCard:
    """Construct a deterministic iterate card from seed + friction.

    Two lightweight patterns for MVP:
    - Close-The-Loop Control (when repetition/confirmation issues are present)
    - Smart Info Capture (fallback)
    """

    # Explicit pattern selection (no scoring). Supports comma-separated combos.
    if pattern:
        raw = pattern.strip().lower()
        keys = [k.strip() for k in raw.replace(" ", "").split(",") if k.strip()]

        def _build_for(k: str) -> Optional[IterateCard]:
            if k in {"constraint-ledger", "ledger", "constraint_ledger"}:
                return build_constraint_ledger(seed, friction)
            if k in {"contrastive-clarify", "contrastive", "clarify"}:
                return build_contrastive_clarify(seed, friction)
            if k in {"exemplar-propose", "exemplar", "propose"}:
                return build_exemplar_propose(seed, friction)
            if k in {"override-hook", "override", "hook"}:
                return build_override_hook(seed, friction)
            if k in {"state-bag", "state", "bag"}:
                return build_state_bag(seed, friction)
            if k in {"slot-filling", "slots", "form"}:
                return build_slot_filling(seed, friction)
            return None

        if len(keys) == 1:
            card = _build_for(keys[0])
        elif len(keys) > 1:
            built = [c for k in keys if (c := _build_for(k)) is not None]
            if built:
                base = built[0]
                def _merge_unique(a: List[str], b: List[str]) -> List[str]:
                    seen = set(a)
                    out = list(a)
                    for item in b:
                        if item not in seen:
                            out.append(item)
                            seen.add(item)
                    return out
                for nxt in built[1:]:
                    base.diagnosis = _merge_unique(base.diagnosis, nxt.diagnosis)
                    base.fix_rules = _merge_unique(base.fix_rules, nxt.fix_rules)
                    base.prompt_patch = _merge_unique(base.prompt_patch, nxt.prompt_patch)
                    base.examples = _merge_unique(base.examples, nxt.examples)
                    base.validation_scenarios = _merge_unique(base.validation_scenarios, nxt.validation_scenarios)
                    base.validation_pass = _merge_unique(base.validation_pass, nxt.validation_pass)
                base.id = "Combined: " + " + ".join(keys)
                card = base
            else:
                card = None
        else:
            card = None
    else:
        card = None

    if card is None and _matches_close_loop(friction):
        id_ = "Close-The-Loop Control"
        diagnosis = [
            "Politeness escalates into repetition (apology/question loops)",
            "Missing state and exit criteria, so conversations drift",
        ]
        fix_rules = [
            "Use at most one apology total",
            "Maintain state: issue, next_step, confirmed=false",
            "Do not repeat a question unless new information was provided",
            "Before closing, confirm resolution explicitly, then recap next_step",
        ]
        prompt_patch = [
            '"Use at most one apology total."',
            '"Maintain state: issue, next_step, confirmed=false."',
            '"Do not repeat a question unless the user provided new information."',
            '"Before closing, ask: Did we fully handle this today? If yes -> set confirmed=true and recap next_step. If no -> ask what is missing and address it."',
            '"Close with a crisp recap + next step, no filler."',
        ]
        examples = [
            "Got it -> exchange for size M in black. I'll email the label now. Did we fully handle this today?",
        ]
        validation_scenarios = [
            "Return: user gives order ID -> provide label; ask one confirmation; close on yes",
            "Exchange (SKU mismatch): propose alternative -> confirm -> recap email/label; no repeated apology",
            "Policy edge: out-of-window -> one apology + store credit -> confirm acceptance -> close",
        ]
        validation_pass = [
            "<= 1 apology; no repeated identical questions",
            "Contains explicit confirmation and final recap",
            "Turns to resolution decrease or stay flat vs baseline",
        ]
    elif card is None:
        id_ = "Smart Info Capture"
        diagnosis = [
            "Multiple re-asks caused by missing upfront data capture",
            "User effort increases when fields are gathered piecemeal",
        ]
        fix_rules = [
            "Extract order_id, item, reason at the start when feasible",
            "Echo captured fields and ask only for missing ones",
            "Prefer structured questions over open-ended repeats",
            "Summarize captured info before next step",
        ]
        prompt_patch = [
            '"Try to extract: order_id, item, reason upfront."',
            '"Echo what is captured; only ask for missing fields."',
            '"Avoid re-asking unless new information appears."',
            '"Before proceeding, recap the captured info and confirm."',
        ]
        examples = [
            "Thanks -> order 12345, item is blue jacket, exchange to M. Missing: return reason. What's the reason?",
        ]
        validation_scenarios = [
            "Direct exchange -> all fields captured -> single confirm",
            "Partial info -> only ask missing fields -> recap",
            "Ambiguous reason -> clarify once, then proceed",
        ]
        validation_pass = [
            "No redundant re-asks; missing-only questions",
            "Single recap + confirmation before next step",
            "Lower average turns vs baseline",
        ]

    # Prepare the final card object if not chosen earlier
    if card is None:
        card = IterateCard(
            id=id_,
            seed=seed,
            friction=friction,
            diagnosis=diagnosis,
            fix_rules=fix_rules,
            prompt_patch=prompt_patch,
            examples=examples,
            validation_scenarios=validation_scenarios,
            validation_pass=validation_pass,
        )

    # ASCII safety: normalize dashes if requested
    if ascii_only:
        def _norm(xs: List[str]) -> List[str]:
            out: List[str] = []
            for s in xs:
                out.append(s.replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'"))
            return out
        card.diagnosis = _norm(card.diagnosis)
        card.fix_rules = _norm(card.fix_rules)
        card.prompt_patch = _norm(card.prompt_patch)
        card.examples = _norm(card.examples)
        card.validation_scenarios = _norm(card.validation_scenarios)
        card.validation_pass = _norm(card.validation_pass)

    return card
