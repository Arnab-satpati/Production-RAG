from __future__ import annotations

import hashlib
import uuid


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def generate_id(prefix: str = "") -> str:
    raw = uuid.uuid4().hex[:12]
    return f"{prefix}:{raw}" if prefix else raw


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]
