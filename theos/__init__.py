"""
THEOS — public package entry point.

When installed via ``pip install theos`` or ``pip install -e .``, the
``setuptools`` ``package-dir`` mapping (in ``pyproject.toml``) resolves
``theos.*`` to the files under ``code/``.  This file is therefore the
same as ``code/__init__.py`` at install time.

For development without installation, import directly from the ``code/``
directory or use the root ``conftest.py`` (pytest) which adds ``code/``
to ``sys.path`` automatically.
"""

# Re-export via the code package so IDE navigation still works when the
# repo is used without installing.
import sys
import os

# Insert code/ only when NOT installed (no-op if already on the path)
_here = os.path.dirname(__file__)
_code = os.path.normpath(os.path.join(_here, "..", "code"))
if _code not in sys.path:
    sys.path.insert(0, _code)

from theos_core import (  # noqa: E402
    TheosCore,
    TheosConfig,
    TheosOutput,
    HaltReason,
    CycleTrace,
)
from theos_system import TheosSystem, create_numeric_system  # noqa: E402
from theos_governor import (  # noqa: E402
    THEOSGovernor,
    TheosDualClockGovernor,
    GovernorConfig,
    EngineOutput,
    GovernorDecision,
    StopReason,
    Posture,
)
from semantic_retrieval import (  # noqa: E402
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
    "TheosCore", "TheosConfig", "TheosOutput", "HaltReason", "CycleTrace",
    "TheosSystem", "create_numeric_system",
    "THEOSGovernor", "TheosDualClockGovernor", "GovernorConfig",
    "EngineOutput", "GovernorDecision", "StopReason", "Posture",
    "EmbeddingAdapter", "MockEmbeddingAdapter", "SemanticRetrieval",
    "VectorStore", "InMemoryVectorStore", "get_vector_store",
    "__version__", "__author__", "__license__", "__patent__",
]
