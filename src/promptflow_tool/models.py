"""Data models for PromptFlow reasoning plans."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SeedQuestion(BaseModel):
    """Represents the initial problem being explored."""

    question: str = Field(..., description="The primary question to answer.")
    context: Optional[str] = Field(
        None, description="Background information establishing the context."
    )
    objective: Optional[str] = Field(
        None, description="Explicit goal associated with the question."
    )
    expected_output: Optional[str] = Field(
        None, description="Anticipated deliverable or format for the answer."
    )


class PromptDraft(BaseModel):
    """Stores a prompt draft used during iteration."""

    text: str = Field(..., description="The textual content of the prompt draft.")
    notes: Optional[str] = Field(
        None, description="Additional guidance or metadata about the draft."
    )


class IterationStep(BaseModel):
    """Captures a single iteration within a reasoning plan."""

    trigger: str = Field(..., description="Situation or feedback that caused change.")
    change: str = Field(..., description="Modification applied during the step.")
    rationale: str = Field(..., description="Reasoning behind the change.")
    outcome: str = Field(..., description="Observed impact of the change.")
