"""
THEOS Session Logger
====================

Persists every MCP session to /logs/ as a structured JSON file.

File naming: session_YYYYMMDD_HHMMSS_{session_id}.json

Each file contains:
  - session metadata (id, started_at, finalized_at)
  - queries: list of full execute_governed_reasoning result dicts
  - wisdom_log: list of log_wisdom entries
  - final_metrics: filled on clean shutdown via atexit

The file is written to disk on every mutation (crash-safe).
"""

import json
import os
from datetime import datetime, timezone


class TheosSessionLogger:
    """Persists a single THEOS MCP session to a JSON file."""

    def __init__(self, log_dir: str, session_id: str, started_at: float):
        self._log_dir = os.path.abspath(log_dir)
        os.makedirs(self._log_dir, exist_ok=True)

        started_dt = datetime.fromtimestamp(started_at, tz=timezone.utc)
        filename = "session_{}_{}.json".format(
            started_dt.strftime("%Y%m%d_%H%M%S"),
            session_id,
        )
        self._path = os.path.join(self._log_dir, filename)

        self._data = {
            "session_id": session_id,
            "started_at": started_dt.isoformat(),
            "finalized_at": None,
            "queries": [],
            "wisdom_log": [],
            "final_metrics": {},
        }
        self._write()

    def log_query(self, result: dict) -> None:
        """Append a complete execute_governed_reasoning result dict."""
        self._data["queries"].append(result)
        self._write()

    def log_wisdom(self, entry: dict) -> None:
        """Append a wisdom entry (from log_wisdom tool)."""
        self._data["wisdom_log"].append(entry)
        self._write()

    def finalize(self, metrics: dict) -> None:
        """Mark session complete with final metrics. Called via atexit."""
        self._data["finalized_at"] = datetime.now(tz=timezone.utc).isoformat()
        self._data["final_metrics"] = metrics
        self._write()

    def _write(self) -> None:
        """Write full session state to disk atomically via a temp-rename."""
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)
            os.replace(tmp, self._path)
        except Exception as exc:
            # Never crash the MCP server over logging
            import sys
            print(f"[theos_logger] write error: {exc}", file=sys.stderr)
