"""
THEOS Plugin - Triadic Reasoning for Transformer Models
Implements triadic reasoning with 50-65% energy savings

Author: Frederick Davis Stalnecker & Manus AI
License: MIT
Version: 1.0.0
"""

from .wrapper import THEOSWrapper
from .core import THEOSConfig, THEOSResponse, CachedState
from .cache import WisdomCache
from .governor import Governor
from .vortex import VortexPair, ConstructiveVortex, DeconstructiveVortex, TriadicReasoner

__version__ = "1.0.0"
__author__ = "Frederick Davis Stalnecker"
__email__ = "guestent@gmail.com"

__all__ = [
    "THEOSWrapper",
    "THEOSConfig",
    "THEOSResponse",
    "CachedState",
    "WisdomCache",
    "Governor",
    "VortexPair",
    "ConstructiveVortex",
    "DeconstructiveVortex",
    "TriadicReasoner",
]
