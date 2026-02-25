# Copyright (c) 2026 Frederick Davis Stalnecker
# Licensed under the MIT License — see LICENSE file for details

"""
theos_dual_clock_governor — backward-compatibility shim
========================================================

All governor logic now lives in :mod:`theos_governor`.
This module re-exports the canonical names so that existing import paths
(especially :mod:`theos_mcp_server`) continue to work unchanged.

Prefer importing directly from ``theos_governor``::

    from theos_governor import THEOSGovernor, GovernorConfig, EngineOutput
"""

from theos_governor import (  # noqa: F401  (re-export)
    THEOSGovernor,
    THEOSGovernor as TheosDualClockGovernor,
    GovernorConfig,
    EngineOutput,
    GovernorDecision,
    StopReason,
    Posture,
)

__all__ = [
    "TheosDualClockGovernor",
    "THEOSGovernor",
    "GovernorConfig",
    "EngineOutput",
    "GovernorDecision",
    "StopReason",
    "Posture",
]
