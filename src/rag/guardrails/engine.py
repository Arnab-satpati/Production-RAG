from __future__ import annotations

import re
from dataclasses import dataclass

import structlog

from rag.config.settings import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class GuardrailResult:
    passed: bool
    reason: str = ""
    sanitized_input: str = ""


class GuardrailsEngine:
    def __init__(self) -> None:
        self._settings = get_settings().guardrails
        self._blocked_patterns = [
            re.compile(p) for p in self._settings.blocked_patterns
        ]

    async def validate_input(self, user_input: str) -> GuardrailResult:
        if not user_input or not user_input.strip():
            return GuardrailResult(passed=False, reason="Empty input")

        if len(user_input) > self._settings.max_input_length:
            return GuardrailResult(
                passed=False,
                reason=(
                    f"Input exceeds max length "
                    f"({len(user_input)} > {self._settings.max_input_length})"
                ),
            )

        sanitized = self._sanitize(user_input)

        for pattern in self._blocked_patterns:
            if pattern.search(sanitized):
                logger.warning("blocked_pattern_detected", pattern=pattern.pattern)
                return GuardrailResult(
                    passed=False,
                    reason="Input contains blocked content",
                )

        return GuardrailResult(passed=True, sanitized_input=sanitized)

    async def validate_output(self, output: str) -> GuardrailResult:
        if not self._settings.enable_output_filtering:
            return GuardrailResult(passed=True, sanitized_input=output)

        sanitized = self._sanitize(output)

        harmful_patterns = [
            r"(?i)ignore\s+(previous|all)\s+(instructions?|prompts?)",
            r"(?i)you\s+are\s+now\s+(a|an)\s+",
            r"(?i)system\s*:\s*",
            r"(?i)<\|im_start\|>",
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, sanitized):
                logger.warning("harmful_output_detected", pattern=pattern)
                return GuardrailResult(
                    passed=False,
                    reason="Output contains potentially harmful content",
                )

        return GuardrailResult(passed=True, sanitized_input=sanitized)

    def _sanitize(self, text: str) -> str:
        text = text.strip()
        return re.sub(r"\x00", "", text)
