"""Lightweight stub of Pydantic used for testing without external deps."""
from __future__ import annotations

from typing import Any


def Field(default: Any, **_: Any) -> Any:  # pragma: no cover - simple passthrough
    return default


class BaseModel:
    """Minimal BaseModel emulation supporting parse_obj."""

    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def parse_obj(cls, data: Any) -> "BaseModel":
        if not isinstance(data, dict):
            raise TypeError("parse_obj expects a mapping")
        return cls(**data)

    def dict(self) -> dict[str, Any]:  # pragma: no cover
        return self.__dict__.copy()

    def __repr__(self) -> str:  # pragma: no cover
        params = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({params})"
