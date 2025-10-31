# PromptKit – Business Quick Start

PromptKit helps you improve how an AI speaks and decides — without needing the original prompt or any coding. You provide two sentences; PromptKit returns a small, clear plan or a single “iterate card” that explains what to change and why.

## What you provide (2 sentences)
- Seed: one sentence describing what the assistant should do and for whom.
- Friction: one sentence describing the biggest failure you see now.

Examples
- Seed: “SnackSmith flavor assistant helps build custom snacks from natural‑language taste descriptions.”
- Friction: “Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override.”

## What you get back
- Iterate Card — a one‑page fix: Diagnosis → Fix (rules + exact lines to add) → Validation (how to test if it worked).
- Plan — a compact explanation: Context, Objective, Flow, Reasoning Path, Output.
- Ticket — a shareable brief that ties a real problem to a testable PromptKit fix.

## When to use which
- If you want a targeted change today: use Iterate Card.
- If you need to align stakeholders: use Plan.
- If you want a brief others can run with: use Ticket.

## How to ask a teammate to run it
Share your Seed and Friction and ask them to run one of these and send you the result.

Iterate Card (choose a pattern if you like)
- constraint‑ledger: keeps a running list of user constraints; avoids contradictions.
- contrastive‑clarify: one either/or question to pin down an ambiguous term.
- exemplar‑propose: two tiny concrete options that both fit the constraints.
- override‑hook: simple staff commands (override/lock/reduce/reset) that apply immediately.

Command examples (your teammate runs these):
- Iterate Card (constraint‑ledger)
  - promptkit iterate --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --pattern constraint-ledger --ascii
- Plan
  - promptkit plan --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --pattern constraint-ledger --ascii
- Ticket
  - promptkit ticket --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --client "SnackSmith" --ascii

## How to use the output (no code)
1) Copy the “Prompt patch” lines into your existing prompt or guideline doc.
2) Use the “Example phrasing” line as a starting sentence.
3) Try the “Validation” scenarios with a colleague or a few customers.
4) If it works, keep it. If not, re‑run with a different pattern (e.g., contrastive‑clarify) and test again.

## Tips
- Keep Seed and Friction to one sentence each.
- Prefer plain language (“repeats apologies; never confirms done”) over technical jargon.
- If your team can’t run commands, just share Seed and Friction and ask for an Iterate Card back.

