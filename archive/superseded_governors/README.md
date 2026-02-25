# Superseded Governor Implementations

These files have been replaced by the unified `code/theos_governor.py`.

| File | Description | Superseded by |
|------|-------------|---------------|
| `theos_governor_phase2.py` | Phase 2 governor with energy accounting, ethical alignment monitoring, UQI. Too complex for the core. | `code/theos_governor.py` |

The v1.4 string-only governor (`THEOSGovernor.evaluate_cycle()`) and the
dual-clock governor (`TheosDualClockGovernor.step()`) are both present in the
unified implementation, which also adds posture states, richer per-score
`EngineOutput`, and session-level audit trails.
