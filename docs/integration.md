---
layout: default
title: LLM Integration Guide — THEOS
---

# LLM Integration Guide

How to wire a real LLM (Claude, GPT-4, or any other) into THEOS as the reasoning engine.

---

## Overview

THEOS ships with `code/theos_llm_reasoning.py` — a complete LLM-backed operator set built on top of the `LLMAdapter` abstraction. This is the fastest path to real dialectical reasoning with a production model.

The same operator contract applies (see [Developer Guide](guide)), but instead of writing rule-based functions, each operator sends a structured prompt to an LLM and parses the response.

---

## Quick Start — Claude

```bash
pip install theos-reasoning anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import sys
sys.path.insert(0, "code")

from llm_adapter import ClaudeAdapter
from theos_llm_reasoning import create_llm_theos_system

# Create a THEOS system backed by Claude
adapter = ClaudeAdapter(model="claude-sonnet-4-6")
system = create_llm_theos_system(adapter=adapter)

result = system.reason("What is the difference between courage and recklessness?")

print(f"Output type: {result.output_type}")
print(f"Confidence:  {result.confidence:.2f}")
print(result.output)
```

---

## Quick Start — GPT-4

```bash
pip install theos-reasoning openai
export OPENAI_API_KEY=sk-...
```

```python
from llm_adapter import GPT4Adapter
from theos_llm_reasoning import create_llm_theos_system

adapter = GPT4Adapter(model="gpt-4-turbo")
system = create_llm_theos_system(adapter=adapter)

result = system.reason("Is efficiency always in tension with effectiveness?")
```

---

## Using the Factory Function

```python
from llm_adapter import get_llm_adapter
from theos_llm_reasoning import create_llm_theos_system

# provider: "claude" | "gpt4" | "mock"
adapter = get_llm_adapter(provider="claude", model="claude-sonnet-4-6")
system = create_llm_theos_system(adapter=adapter)
```

---

## Implementing Your Own LLM Adapter

If you are integrating a model not covered by the built-in adapters (Llama, Mistral, Gemini, a local model, etc.), subclass `LLMAdapter`:

```python
from llm_adapter import LLMAdapter, LLMResponse

class MyModelAdapter(LLMAdapter):

    def __init__(self):
        super().__init__(model_name="my-model")
        self.client = MyModelClient()

    def _call_llm(self, prompt, system_prompt, temperature, max_tokens) -> LLMResponse:
        response = self.client.generate(
            prompt=prompt,
            system=system_prompt or "",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.text,
            tokens_used=response.token_count,
            model=self.model_name,
            stop_reason=response.finish_reason,
        )

    def _count_tokens(self, text: str) -> int:
        return len(text) // 4  # approximate
```

Then use it anywhere an `LLMAdapter` is expected:

```python
system = create_llm_theos_system(adapter=MyModelAdapter())
```

---

## How LLM Operators Work

The `theos_llm_reasoning.py` module translates the THEOS operator contract into structured LLM prompts. The left and right engines differ **only in their system prompt**:

- **Left engine (constructive):** `"Build the strongest coherent case for the best answer. Your role is to construct, not criticize."`
- **Right engine (adversarial):** `"Your role is to stress-test any argument and find its weaknesses. Build the strongest case against whatever the left engine would say."`

The self-reflection prompt (second inner pass) is: `"You previously concluded: {prior_conclusion}. Does that conclusion hold under scrutiny? Refine it or defend it with stronger reasoning."`

This structure is what produces the structural depth the single-pass answer misses.

---

## MCP Server — Claude Desktop Integration

THEOS can be embedded directly into Claude Desktop via the Model Context Protocol (MCP).

### Install

```bash
pip install theos-reasoning mcp
```

### Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "theos": {
      "command": "python",
      "args": ["/path/to/THEOS/code/theos_mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `execute_governed_reasoning` | Run a query through the full dual-engine wringer |
| `get_governor_status` | Return current governor posture and contradiction budget |
| `log_wisdom` | Manually deposit a lesson into the wisdom store |

### Example (from Claude Desktop)

Once configured, you can invoke THEOS directly from a Claude conversation:

> "Use THEOS to reason about whether efficiency is always in tension with effectiveness."

Claude will invoke the `execute_governed_reasoning` tool, run the dual-engine loop, and return the structured output.

---

## Token Cost

LLM-backed THEOS is **more expensive than single-pass** due to multiple LLM calls per query:

| Architecture | LLM calls per query | Token cost (approx) |
|-------------|--------------------|--------------------|
| Single-pass (SP) | 1 | ~400–600 tokens |
| THEOS (2 engines × 2 inner passes × 1–3 outer passes) | 6–12 | ~7,600–8,100 tokens |

Cost is 12–20× higher than single-pass in the current overlay architecture.

**When is it worth it?** For open-ended conceptual questions where structural depth matters — strategy, ethics, diagnosis, research, legal reasoning. Not for factual lookups or simple classification tasks.

**The native architecture** (planned) will reduce cost to approximately 0.5× single-pass through KV cache reuse. This remains theoretical; the overlay architecture is what exists today.

---

## Best Practices

**Choose questions where dialectical tension adds value:**
- Open-ended conceptual questions (preferred)
- Decisions with genuine trade-offs
- Questions where the framing itself is part of the answer

**Questions THEOS is not optimized for:**
- Factual lookups ("What is the capital of France?")
- Simple arithmetic
- Tasks requiring a single definitive answer with no ambiguity

**Handle `"disagreement"` outputs explicitly:**
```python
result = system.reason(query)
if result.output_type == "disagreement":
    # Present both perspectives to the user
    print("This question has no single answer without choosing a frame:")
    print("  Frame A:", result.output["left"])
    print("  Frame B:", result.output["right"])
```

**Budget for iterative reasoning:**
```python
from theos_core import TheosConfig

# For expensive production use — cap at 3 outer passes
config = TheosConfig(max_wringer_passes=3, budget=15000)
```

---

*[API Reference](api) · [Developer Guide](guide) · [Troubleshooting](troubleshooting)*
