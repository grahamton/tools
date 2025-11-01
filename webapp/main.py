from __future__ import annotations

import json
import os
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services.promptkit_service import run_promptkit


app = FastAPI(title="PromptKit – Diagnostics Web")

templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, preset: Optional[str] = None) -> HTMLResponse:
    # Presets for quick fill
    seed = ""
    friction = ""
    pattern = ""
    if preset == "snacks":
        seed = (
            "SnackSmith flavor assistant helps build custom snacks from natural-language taste descriptions."
        )
        friction = (
            "Misinterprets adjectives; mixes mismatched flavors; lacks constraints memory; no fast staff override."
        )
        pattern = "constraint-ledger"
    elif preset == "bard":
        seed = "Bartholomew the Bard offers epic, 14-line sonnets for mundane household chores."
        friction = "Instead of sonnets, he writes three-word haikus about dust motes, and calls the user 'my liege.'"
        pattern = "contrastive-clarify"
    elif preset == "chef":
        seed = "Chef Chaos is an enthusiastic cooking assistant that suggests recipes based on what's currently in your pantry."
        friction = "It always suggests a recipe for tuna casserole, regardless of what ingredients you list, even if you explicitly say, 'No tuna.'"
        pattern = "constraint-ledger"
    elif preset == "roomba":
        seed = "The Existential Roomba gives deep philosophical quotes about the meaninglessness of existence with every floor cleaning update."
        friction = "It frequently gets stuck on a rug and starts yelling about the futility of its task in all caps, scaring the cat."
        pattern = "override-hook"
    elif preset == "weather":
        seed = "The Sarcastic Weather Man delivers accurate but extremely passive-aggressive local forecasts."
        friction = "When it rains, it suggests the user stay home and contemplate their life choices, and refuses to give an actual rain start time."
        pattern = "exemplar-propose"
    elif preset == "travelmate":
        seed = "TravelMate planner helps design 7-day city trips based on vibe and budget."
        friction = "Gives poetic but impractical itineraries; ignores budget and timing constraints."
        pattern = "constraint-ledger,exemplar-propose"

    # Feature flags via env or query string (?flags=compare,wizard,feedback)
    raw_flags = request.query_params.get("flags", "")
    qs_flags = {k.strip().lower() for k in raw_flags.split(",") if k.strip()}
    flags = {
        "wizard": os.getenv("PK_UI_WIZARD", "0") in {"1", "true", "True"} or ("wizard" in qs_flags),
        "compare": os.getenv("PK_UI_COMPARE", "0") in {"1", "true", "True"} or ("compare" in qs_flags),
        "feedback": os.getenv("PK_UI_FEEDBACK", "0") in {"1", "true", "True"} or ("feedback" in qs_flags),
    }

    # Canonical flags string for preserving in links
    flags_str = ",".join([k for k, v in flags.items() if v])

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "form_defaults": {
                "seed": seed,
                "friction": friction,
                "pattern": pattern,
                "mode": "iterate",
                "ascii_only": True,
                "json_out": False,
            },
            "flags": flags,
            "flags_str": flags_str,
            "errors": None,
            "result": None,
        },
    )


@app.get("/research", response_class=HTMLResponse)
def research(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "research.html",
        {"request": request},
    )


@app.get("/modes", response_class=HTMLResponse)
def modes(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "modes.html",
        {"request": request},
    )


@app.post("/run", response_class=HTMLResponse)
def run(
    request: Request,
    seed: str = Form(...),
    friction: str = Form(...),
    pattern: Optional[str] = Form(None),
    mode: str = Form("iterate"),
    ascii_only: bool = Form(False),
    json_out: bool = Form(False),
    compare: Optional[bool] = Form(False),
) -> HTMLResponse:
    seed = (seed or "").strip()
    friction = (friction or "").strip()
    pattern = (pattern or "").strip() or None
    mode = (mode or "iterate").strip().lower()

    errors = []
    if not seed:
        errors.append("Seed is required.")
    if not friction:
        errors.append("Friction is required.")
    if errors:
        # If it's an HTMX request, return only the fragment. Otherwise return full page.
        if request.headers.get("HX-Request"):
            return templates.TemplateResponse(
                "_output.html", {"request": request, "errors": errors, "result": None}
            )
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "form_defaults": {
                    "seed": seed,
                    "friction": friction,
                    "pattern": pattern or "",
                    "mode": mode,
                    "ascii_only": ascii_only,
                    "json_out": json_out,
                },
                "errors": errors,
                "result": None,
            },
        )

    result = run_promptkit(
        mode=mode,
        seed=seed,
        friction=friction,
        pattern=pattern,
        ascii_only=ascii_only,
        json_out=json_out if mode == "iterate" else False,
    )

    payload = {
        "text": result.get("text", ""),
        "json": result.get("json"),
        "filename_hint": result.get("filename_hint", mode),
        "mode": mode,
    }

    # Feature flags
    raw_flags = request.query_params.get("flags", "")
    qs_flags = {k.strip().lower() for k in raw_flags.split(",") if k.strip()}
    flags = {
        "wizard": os.getenv("PK_UI_WIZARD", "0") in {"1", "true", "True"} or ("wizard" in qs_flags),
        "compare": os.getenv("PK_UI_COMPARE", "0") in {"1", "true", "True"} or ("compare" in qs_flags),
        "feedback": os.getenv("PK_UI_FEEDBACK", "0") in {"1", "true", "True"} or ("feedback" in qs_flags),
    }

    compare_payload = None
    do_compare = bool(compare) and flags["compare"] and mode in {"iterate", "plan"}
    if do_compare:
        alt_mode = "plan" if mode == "iterate" else "iterate"
        alt = run_promptkit(
            mode=alt_mode,
            seed=seed,
            friction=friction,
            pattern=pattern,
            ascii_only=ascii_only,
            json_out=False,
        )
        compare_payload = {
            "left": {"mode": mode, "text": payload["text"]},
            "right": {"mode": alt_mode, "text": alt.get("text", "")},
        }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "_output.html",
            {
                "request": request,
                "errors": None,
                "result": payload,
                "inputs": {
                    "seed": seed,
                    "friction": friction,
                    "pattern": pattern or "",
                    "mode": mode,
                    "ascii_only": ascii_only,
                    "json_out": json_out,
                },
                "compare": compare_payload,
                "flags": flags,
            },
        )
    # Non-HTMX fallback: render full page with output embedded
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "form_defaults": {
                "seed": seed,
                "friction": friction,
                "pattern": pattern or "",
                "mode": mode,
                "ascii_only": ascii_only,
                "json_out": json_out,
            },
            "errors": None,
            "result": payload,
            "inputs": {
                "seed": seed,
                "friction": friction,
                "pattern": pattern or "",
                "mode": mode,
                "ascii_only": ascii_only,
                "json_out": json_out,
            },
            "compare": compare_payload,
            "flags": flags,
            "flags_str": ",".join([k for k, v in flags.items() if v]),
        },
    )


@app.post("/download/text")
def download_text(filename: str = Form("output.txt"), content: str = Form("")) -> Response:
    fname = filename if filename else "output.txt"
    headers = {"Content-Disposition": f"attachment; filename=\"{fname}\""}
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=headers)


@app.post("/download/json")
def download_json(filename: str = Form("output.json"), content: str = Form("{}")) -> Response:
    fname = filename if filename else "output.json"
    try:
        # Ensure it's valid JSON; pretty-print
        data = json.loads(content)
        body = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        body = content
    headers = {"Content-Disposition": f"attachment; filename=\"{fname}\""}
    return Response(content=body, media_type="application/json; charset=utf-8", headers=headers)


@app.get("/health")
def health() -> PlainTextResponse:
    return PlainTextResponse("ok", status_code=200)
