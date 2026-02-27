#!/usr/bin/env python3
"""
LLM Adapter - Abstraction Layer for Any LLM
============================================

This module provides an abstract interface for integrating any LLM into THEOS.
Supports:
- Claude (Anthropic)
- GPT-4 (OpenAI)
- Llama (Meta)
- Any other LLM with an API

The adapter handles:
- Prompt construction
- Response parsing
- Token counting
- Error handling
- Rate limiting

Author: Frederick Davis Stalnecker
Date: February 22, 2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Structured response from an LLM."""

    content: str
    tokens_used: int
    model: str
    stop_reason: str | None = None
    confidence: float | None = None


class LLMAdapter(ABC):
    """
    Abstract base class for LLM integration.

    Implementations should override:
    - _call_llm: Make the actual API call
    - _count_tokens: Count tokens in prompt/response
    - _parse_response: Parse LLM response
    """

    def __init__(self, model_name: str, api_key: str | None = None):
        """
        Initialize LLM adapter.

        Args:
            model_name: Name of the model (e.g., "claude-3-opus", "gpt-4")
            api_key: API key for the LLM service
        """
        self.model_name = model_name
        self.api_key = api_key
        self.total_tokens_used = 0
        self.total_calls = 0

    def reason(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Run reasoning on a prompt.

        Args:
            prompt: The reasoning prompt
            system_prompt: Optional system context
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length

        Returns:
            LLMResponse with content and metadata
        """
        # Call the LLM
        response = self._call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Track usage
        self.total_tokens_used += response.tokens_used
        self.total_calls += 1

        return response

    @abstractmethod
    def _call_llm(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Make the actual API call to the LLM."""
        pass

    @abstractmethod
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass

    def get_statistics(self) -> dict[str, Any]:
        """Get usage statistics."""
        return {
            "model": self.model_name,
            "total_calls": self.total_calls,
            "total_tokens_used": self.total_tokens_used,
            "average_tokens_per_call": (
                self.total_tokens_used / self.total_calls if self.total_calls > 0 else 0
            ),
        }


class ClaudeAdapter(LLMAdapter):
    """
    Adapter for Claude (Anthropic).

    Uses the Claude API to provide reasoning engines for THEOS.
    """

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude adapter.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Claude model to use
        """
        super().__init__(model_name=model, api_key=api_key)

        # Import here to avoid hard dependency
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

    def _call_llm(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call Claude API."""

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Call Claude
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            system=system_prompt or "",
            temperature=temperature,
            messages=messages,
        )

        # Extract content
        content = response.content[0].text if response.content else ""

        # Count tokens (Claude provides this in response)
        tokens_used = response.usage.output_tokens + response.usage.input_tokens

        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            model=self.model_name,
            stop_reason=response.stop_reason,
        )

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (Claude uses ~4 chars per token on average)."""
        return len(text) // 4


class GPT4Adapter(LLMAdapter):
    """
    Adapter for GPT-4 (OpenAI).

    Uses the OpenAI API to provide reasoning engines for THEOS.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4-turbo"):
        """
        Initialize GPT-4 adapter.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: GPT model to use
        """
        super().__init__(model_name=model, api_key=api_key)

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

    def _call_llm(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call GPT-4 API."""

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Call GPT-4
        response = self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )

        # Extract content
        content = response.choices[0].message.content if response.choices else ""

        # Count tokens
        tokens_used = response.usage.completion_tokens + response.usage.prompt_tokens

        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            model=self.model_name,
            stop_reason=response.choices[0].finish_reason if response.choices else None,
        )

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (GPT uses ~4 chars per token on average)."""
        return len(text) // 4


class MockLLMAdapter(LLMAdapter):
    """
    Mock LLM for testing.

    Returns predetermined responses without making API calls.
    """

    def __init__(self, model_name: str = "mock-llm"):
        """Initialize mock adapter."""
        super().__init__(model_name=model_name)
        self.call_count = 0

    def _call_llm(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Return mock response."""
        self.call_count += 1

        # Generate deterministic response based on prompt
        if "constructive" in prompt.lower():
            content = f"[Mock Constructive Response {self.call_count}] Building strongest case for the proposition."
        elif "critical" in prompt.lower():
            content = (
                f"[Mock Critical Response {self.call_count}] Testing weaknesses and exposing risks."
            )
        else:
            content = f"[Mock Response {self.call_count}] Reasoning about the query."

        return LLMResponse(
            content=content,
            tokens_used=len(content) // 4,
            model=self.model_name,
            stop_reason="end_turn",
        )

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(text) // 4


def get_llm_adapter(
    provider: str = "claude",
    api_key: str | None = None,
    model: str | None = None,
) -> LLMAdapter:
    """
    Factory function to get an LLM adapter.

    Args:
        provider: "claude", "gpt4", or "mock"
        api_key: API key for the provider
        model: Specific model to use

    Returns:
        LLMAdapter instance
    """
    if provider.lower() == "claude":
        return ClaudeAdapter(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
    elif provider.lower() == "gpt4":
        return GPT4Adapter(api_key=api_key, model=model or "gpt-4-turbo")
    elif provider.lower() == "mock":
        return MockLLMAdapter(model_name=model or "mock-llm")
    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    # Test the adapter
    print("Testing LLM Adapter...")

    # Try with mock first (no API key needed)
    adapter = get_llm_adapter("mock")

    response = adapter.reason(
        prompt="What is 2+2?",
        system_prompt="You are a helpful assistant.",
    )

    print(f"Response: {response.content}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Statistics: {adapter.get_statistics()}")
