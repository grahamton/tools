# PromptKit Roadmap

This document tracks future work after the current MVP (iterate / plan / ticket).

## Themes
- **Input depth** — accept richer context (draft prompts, transcripts) without losing determinism.
- **Reasoning clarity** — extend artifacts with causal chains, test plans, and metrics.
- **Delivery surfaces** — make it easy to run from CLI, notebooks, or hosted apps.
- **Trust & validation** — help teams prove a change works before shipping.

## Near-Term (Next Iteration)
- **Prompt ingestion mode**: optional `--draft path/to/prompt.txt` so PromptKit can reference existing instructions when generating cards/plans; keep deterministic heuristics.
- **Model guidance field**: add a short “Model considerations” section to iterate cards (e.g., GPT‑4 vs. local LLM limits, latency implications).
- **Seed/Friction library**: allow `promptkit ticket --template snacks` to preload reusable briefs.
- **ASCII default toggle**: infer terminal encoding; auto-switch to ASCII when needed.
- **Combined pattern cards**: support `--pattern constraint-ledger,contrastive-clarify` to merge behaviors into one output.
- **Unit tests**: add tests that assert word counts, section ordering, and deterministic output for sample inputs.

## Mid-Term (2–4 Iterations)
- **Reasoning depth options**: `--mode cot` to include step-by-step reasoning or chain-of-thought hints without leaking private context.
- **Validation scripts**: generate lightweight test scripts (e.g., conversation prompts) so users can copy/paste straight into chat tools.
- **Metrics hooks**: produce a “what to measure” mini-section (conversion, handle time, CSAT proxy).
- **Session memory patterns**: add dedicated cards for “state bag,” “timeline guard,” “handoff protocol.”
- **Integration examples**: show how to call PromptKit from notebooks or simple web UI (Streamlit/FastAPI).
- **PowerShell + Bash parity**: add a cross-platform runner shell script; include package entry for `promptkit-run` console script.

## Long-Term (Vision)
- **Workspace analyzer**: read a prompt repo and suggest seeds/frictions automatically.
- **LLM-assisted variants**: optional flag to call an LLM for richer drafts while retaining deterministic core.
- **Prompt diffing**: compare before/after instructions and highlight reasoning-based deltas.
- **Team workspace**: export iterate cards and plans to shared formats (Notion, Confluence, Slack).
- **Automated validation**: integrate with synthetic conversation generators to test revised prompts at scale.

## Infrastructure / Quality
- Continuous integration: lint, type-check (mypy), run `pytest` for deterministic tests.
- Packaging: publish to PyPI once CLI stabilizes; provide versioned changelog.
- Telemetry hooks (optional): track which patterns users run (opt-in) to inform defaults.
- Documentation site: host README, guides, roadmap with mkdocs or similar.

## Research Questions
- How much context can we ingest before determinism breaks? (Explore chunking/extraction heuristics.)
- What minimal pattern set covers 80% of prompt failures? (Gather real use cases.)
- How to represent “reasoning quality” numerically without relying on hidden CoT?
- Where should PromptKit stop vs. handing off to LLM-based rewriting tools?

## Tracking Suggestions
- Use GitHub Projects or a Kanban board with columns: Backlog, Next Iteration, In Progress, Demo Ready.
- Create labels for `pattern`, `integration`, `docs`, `research` to group issues.
- Schedule a short planning checkpoint after each demo to re-rank features.

## Interactive Plan Mode (Future Work)

**Goal**  
Transform the Plan layer into an interactive testing loop where users iteratively diagnose and fix broken prompts.

**Key Objectives**
- Let users run the initial broken prompt directly from the CLI to observe reasoning and failure modes.
- Capture feedback and produce one *atomic* fix per iteration.
- Validate fixes against pre-defined test cases in real time.
- Record reasoning evidence and outcomes to persistent artifacts.

**Interactive Loop**
1. **Probe** – user provides input and observes the model’s reasoning and output.
2. **Diagnose** – system identifies mismatches (tone, logic, pacing, grounding, success checks).
3. **Rule Proposal** – system proposes a single, deterministic fix with a brief rationale.
4. **Preview & Validate** – user previews new prompt, runs validation tests, sees pass/fail.
5. **Commit or Rollback** – successful rules are appended to `ruleset.md`; failed ones revert.

**Artifacts**
- `plan_state.json` – tracks session state, model settings, last rule.
- `ruleset.md` – cumulative list of rules with short rationales.
- `tests.yaml` – stores validation inputs and expectations.

**CLI Commands (planned)**

