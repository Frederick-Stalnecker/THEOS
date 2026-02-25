# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License

"""
LLM Interface for THEOS Validation Experiments
================================================

This module provides a clean adapter between the experiment framework
and any LLM backend. Supports:

- MockLLM: Deterministic, no API required — for testing the framework
- AnthropicLLM: Claude (claude-sonnet-4-6 or similar) via anthropic SDK
- OpenAILLM: GPT-4 via openai SDK

Design principle: The experiment results must not depend on which LLM
is used for the test. The THEOS methodology should show improvement
across different underlying models. If it only works on one model,
that is a finding worth reporting.

Usage:
    from experiments.llm_interface import get_llm

    llm = get_llm("anthropic", api_key="...")
    response = llm.complete("What is the difference between X and Y?")
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


# ─── Response dataclass ──────────────────────────────────────────────────────

@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0


# ─── Base class ──────────────────────────────────────────────────────────────

class LLMInterface(ABC):
    """Abstract base for all LLM backends."""

    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 512) -> LLMResponse:
        """Generate a completion for the given prompt."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model identifier."""
        ...


# ─── Mock LLM (for framework testing, no API required) ───────────────────────

class MockLLM(LLMInterface):
    """
    Deterministic mock LLM for testing the experiment framework.

    Returns structured placeholder responses that exercise the full
    experiment pipeline without requiring an API key.

    IMPORTANT: Results from MockLLM are NOT evidence for or against THEOS.
    They only verify that the experiment harness is working correctly.
    """

    def __init__(self, response_length: int = 3):
        self._response_length = response_length
        self._call_count = 0

    @property
    def model_name(self) -> str:
        return "mock-llm-v1"

    def complete(self, prompt: str, max_tokens: int = 512) -> LLMResponse:
        self._call_count += 1
        # Generate a deterministic response based on prompt content
        words = prompt.lower().split()
        key_words = [w for w in words if len(w) > 4][-3:] if words else ["concept"]
        mock_text = (
            f"Based on the prompt, the key insight concerns {', '.join(key_words)}. "
            f"This appears to involve a relationship between distinct but related concepts. "
            f"The deeper structure suggests an interaction effect that single-pass "
            f"analysis would miss. [Mock response #{self._call_count}]"
        )
        return LLMResponse(
            text=mock_text,
            model=self.model_name,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(mock_text.split()),
            latency_ms=1.0,
        )


# ─── Anthropic / Claude ───────────────────────────────────────────────────────

class AnthropicLLM(LLMInterface):
    """
    Claude via the Anthropic SDK.

    Install: pip install anthropic
    API key: set ANTHROPIC_API_KEY environment variable or pass directly.

    Recommended model: claude-sonnet-4-6 (latest capable model as of 2026-02)
    """

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package required: pip install anthropic"
            ) from exc

        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Anthropic API key required. Pass api_key= or set ANTHROPIC_API_KEY."
            )
        self._model = model or self.DEFAULT_MODEL
        self._client = anthropic.Anthropic(api_key=self._api_key)

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, prompt: str, max_tokens: int = 512) -> LLMResponse:
        import anthropic

        t0 = time.time()
        try:
            msg = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text
            latency = (time.time() - t0) * 1000
            return LLMResponse(
                text=text,
                model=self._model,
                prompt_tokens=msg.usage.input_tokens,
                completion_tokens=msg.usage.output_tokens,
                latency_ms=latency,
            )
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e


# ─── OpenAI / GPT-4 ──────────────────────────────────────────────────────────

class OpenAILLM(LLMInterface):
    """
    GPT-4 via the OpenAI SDK.

    Install: pip install openai
    API key: set OPENAI_API_KEY environment variable or pass directly.
    """

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package required: pip install openai"
            ) from exc

        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OpenAI API key required. Pass api_key= or set OPENAI_API_KEY."
            )
        self._model = model or self.DEFAULT_MODEL
        from openai import OpenAI
        self._client = OpenAI(api_key=self._api_key)

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, prompt: str, max_tokens: int = 512) -> LLMResponse:
        t0 = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content
            latency = (time.time() - t0) * 1000
            usage = response.usage
            return LLMResponse(
                text=text,
                model=self._model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                latency_ms=latency,
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e


# ─── Factory ─────────────────────────────────────────────────────────────────

def get_llm(
    backend: str = "mock",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMInterface:
    """
    Get an LLM instance by backend name.

    Args:
        backend: "mock" | "anthropic" | "openai"
        api_key: Optional API key (otherwise reads from environment)
        model: Optional model override

    Returns:
        LLMInterface instance ready to use

    Examples:
        # Framework testing — no API needed
        llm = get_llm("mock")

        # Real experiment with Claude
        llm = get_llm("anthropic", api_key="sk-ant-...")

        # Real experiment with GPT-4
        llm = get_llm("openai", api_key="sk-...")
    """
    backend = backend.lower().strip()
    if backend == "mock":
        return MockLLM()
    elif backend in ("anthropic", "claude"):
        return AnthropicLLM(api_key=api_key, model=model)
    elif backend in ("openai", "gpt4", "gpt-4"):
        return OpenAILLM(api_key=api_key, model=model)
    else:
        raise ValueError(
            f"Unknown backend '{backend}'. Choose: mock | anthropic | openai"
        )
