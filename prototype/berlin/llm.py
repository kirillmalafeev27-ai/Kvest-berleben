"""Абстракция над LLM. Офлайн → mode='stub' (роли работают на правилах).
При наличии ANTHROPIC_API_KEY и пакета `anthropic` → mode='claude'.

Используется в design-промптах: Parser (temp 0, строгий JSON), Narrator (temp ~0.8),
Analyst (temp 0). Системные промпты — в соответствующих модулях.
"""
from __future__ import annotations

import os


# Дефолтная модель — последняя доступная (см. указания по моделям Claude).
DEFAULT_MODEL = os.environ.get("BERLIN_CLAUDE_MODEL", "claude-opus-4-8")


class LLM:
    def __init__(self, force_stub: bool = False):
        self.mode = "stub"
        self._client = None
        if force_stub:
            return
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return
        try:
            import anthropic  # type: ignore
            self._client = anthropic.Anthropic(api_key=key)
            self.mode = "claude"
        except Exception:
            self.mode = "stub"

    @property
    def available(self) -> bool:
        return self.mode == "claude"

    def complete(self, system: str, user: str, *, temperature: float = 0.0,
                 max_tokens: int = 700, model: str | None = None) -> str:
        """Один вызов чата. В stub-режиме не вызывается (роли идут по правилам)."""
        if not self.available:
            raise RuntimeError("LLM недоступен (stub-режим)")
        msg = self._client.messages.create(  # type: ignore[union-attr]
            model=model or DEFAULT_MODEL,
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return "".join(getattr(b, "text", "") for b in msg.content)
