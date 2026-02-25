"""
THEOS — Temporal Hierarchical Emergent Optimization System
==========================================================

Runtime AI governance framework implementing dual-engine dialectical
reasoning with a contradiction-bounded governor.

**Zero external dependencies.  Python 3.10+.**

Quick start::

    from theos import TheosSystem, TheosConfig, create_numeric_system

    cfg    = TheosConfig(max_cycles=5)
    system = create_numeric_system(cfg)
    result = system.reason("Should we proceed?")
    print(result.output, result.confidence)

Package layout
--------------
* ``theos_core``     — ``TheosCore``, the I→A→D→I cycle engine
* ``theos_system``   — ``TheosSystem``, high-level wrapper with persistence
* ``theos_governor`` — ``THEOSGovernor``, unified dual-clock governor
* ``semantic_retrieval`` — ``VectorStore``, embeddings, cosine search
* ``llm_adapter``    — ``LLMAdapter`` ABC for Claude / GPT-4 / Llama
* ``theos_mcp_server``   — MCP stdio server (requires ``pip install mcp``)
"""

from .theos_core import (
    TheosCore,
    TheosConfig,
    TheosOutput,
    HaltReason,
    CycleTrace,
)
from .theos_system import TheosSystem, create_numeric_system
from .theos_governor import (
    THEOSGovernor,
    TheosDualClockGovernor,   # backward-compat alias
    GovernorConfig,
    EngineOutput,
    GovernorDecision,
    StopReason,
    Posture,
)
from .semantic_retrieval import (
    EmbeddingAdapter,
    MockEmbeddingAdapter,
    SemanticRetrieval,
    VectorStore,
    InMemoryVectorStore,
    get_vector_store,
)

__version__  = "1.0.0"
__author__   = "Frederick Davis Stalnecker"
__license__  = "MIT"
__patent__   = "USPTO #63/831,738"

__all__ = [
    # ── Core ──────────────────────────────────────────────────────────────
    "TheosCore",
    "TheosConfig",
    "TheosOutput",
    "HaltReason",
    "CycleTrace",
    # ── System ────────────────────────────────────────────────────────────
    "TheosSystem",
    "create_numeric_system",
    # ── Governor ──────────────────────────────────────────────────────────
    "THEOSGovernor",
    "TheosDualClockGovernor",
    "GovernorConfig",
    "EngineOutput",
    "GovernorDecision",
    "StopReason",
    "Posture",
    # ── Retrieval ─────────────────────────────────────────────────────────
    "EmbeddingAdapter",
    "MockEmbeddingAdapter",
    "SemanticRetrieval",
    "VectorStore",
    "InMemoryVectorStore",
    "get_vector_store",
    # ── Metadata ──────────────────────────────────────────────────────────
    "__version__",
    "__author__",
    "__license__",
    "__patent__",
]
