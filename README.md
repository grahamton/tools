# PromptKit

Explain-first prompt iteration toolkit (MVP).

## Overview
PromptKit helps you improve prompts by explaining why each change is made. It outputs small, deterministic artifacts:
- Iterate Card: Diagnosis -> Fix -> Validation
- Plan: Context, Objective, Flow, Reasoning Path, Output
- Ticket: A brief template tying a real problem to a testable PromptKit fix

> Note: This is an exploratory test product I'm using to learn and experiment with tooling. It's free to use and learn from in the same way I am—and my boss Dan should definitely check it out for upcoming prompt work.

## Scope
- PromptKit is a prompt system diagnostic and optimization framework, not a syntax fixer.
- It compares intended behavior vs. actual outcomes, surfacing breakdowns in reasoning, tone, grounding, control flow, and success checks.
- Two lenses:
  - **Prompt Repair Layer** — detect & correct flaws inside a single prompt or template.
  - **System Diagnostic Layer** — model how prompts behave in production flows (multi-step agents, retrieval pipelines, chat orchestration) to spot control gaps.
- Core capabilities today and on the roadmap include intent-to-behavior comparison, structured defect logging, delta planning, grounding validation, tone/pacing review, and session replay with reasoning traces.
- Philosophy: *prompts are systems, not sentences*. PromptKit aims to bridge prompt authorship, system design, and operational reliability.

## Install
- Editable install (recommended):
  - `python -m pip install -e .`

## Commands
### iterate
Generate a single Iterate Card from a seed and a friction point.
- Usage:
  - `promptkit iterate --seed "..." --friction "..." [--pattern <name>] [--ascii] [--json]`
- Patterns (no scoring): `constraint-ledger`, `contrastive-clarify`, `exemplar-propose`, `override-hook`
- Example (SnackSmith):
  - `promptkit iterate --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --pattern constraint-ledger --ascii`

### plan
Produce a compact plan that shows causal reasoning behind the change.
- Usage:
  - `promptkit plan --seed "..." --friction "..." [--pattern <name>] [--ascii]`
- Example (SnackSmith):
  - `promptkit plan --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --pattern constraint-ledger --ascii`

### ticket
Print a filled PromptKit ticket to frame work quickly.
- Usage:
  - `promptkit ticket --seed "..." --friction "..." [--client "..."] [--prompt_brief "..."] [--real_problem "..."] [--test_problem "..."] [--goal "..."] [--success "..."]... [--ascii]`
- Example (SnackSmith minimal):
  - `promptkit ticket --seed "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions." --friction "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override." --client "SnackSmith" --ascii`

## Patterns (no scoring)
- constraint-ledger: Keep a running list of constraints (include/avoid/not-too/vibes); echo and confirm before action.
- contrastive-clarify: Ask one either/or to disambiguate a term; reflect choice; proceed.
- exemplar-propose: Offer two tiny, concrete options that fit constraints; let the user pick or tweak.
- override-hook: Simple staff commands (override/lock/reduce/reset); apply immediately and echo.

## Notes
- Use `--ascii` to avoid Unicode rendering issues in terminals.
- In PowerShell, prefer double quotes around arguments; escape embedded double quotes.

## Status
- iterate, plan, and ticket commands are implemented. More patterns and helpers can be added as needed.

## Business Runner (PowerShell)
- From the repo root, run: `./promptkit-run.ps1`
- It will ask for:
  - Seed (one sentence)
  - Friction (one sentence)
  - Optional pattern (press Enter to auto)
- It prints an Iterate Card to your terminal (ASCII-safe). If the `promptkit` CLI is not installed, it runs from local source automatically.
- If you hit an execution policy warning, you can run once with: `powershell -ExecutionPolicy Bypass -File ./promptkit-run.ps1`

Troubleshooting
- "Python not found": install Python 3.9+ or install the CLI: `python -m pip install -e .`
- Missing dependency `typer`: `python -m pip install typer` (or install the CLI with `-e .`).
- Command not recognized `promptkit`: run the script again (it will use local source), or install the CLI: `python -m pip install -e .`

## Business Quick Start
- Provide two short lines (no tech needed):
  - Seed: what the assistant does and for whom (one sentence).
  - Friction: the biggest failure right now (one sentence).
- Pick the output you want:
  - Iterate Card: one targeted fix with how to validate it.
  - Plan: a clear, one‑page explanation of why the fix works.
  - Ticket: a brief to share with your team to kick off work.
- Ask a teammate to run the command examples above and send you the output, or copy/paste the output lines into your existing prompt.

See the step-by-step business guide: `GUIDE_BUSINESS.md`.

## Demo Playbook
- Want to show PromptKit live? Follow `DEMO_GUIDE.md` for a 5–7 minute walkthrough covering Iterate Card, Plan, Ticket, and the business runner.

## Roadmap
- Future work (prompt ingestion, model considerations, validation tooling, team workflows) is tracked in `ROADMAP.md`.
