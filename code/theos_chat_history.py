# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Chat History — Session Persistence
==========================================

Persists conversation sessions to disk so that they can be recalled
after the process restarts or the window is closed.

Key Features:
1. Session management: create, load, list, and delete named sessions
2. Turn recording: append user/assistant turns with timestamps
3. Last-session recall: ``get_last_session()`` returns the most-recent
   session — solving the "it just vanished" problem
4. Keyword search across all persisted sessions

Each session is stored as a single JSON file in a configurable
directory (default: ``~/.theos/chat_history/``).  Only Python's
standard library is used.

Usage::

    history = ChatHistory()                      # uses default dir
    sid = history.new_session(label="my chat")
    history.add_turn(sid, "user", "Hello!")
    history.add_turn(sid, "assistant", "Hi there!")

    # Later — even after restart:
    session = history.get_last_session()         # get it back
    for turn in session["turns"]:
        print(turn["role"], ":", turn["content"])

Author: Frederick Davis Stalnecker
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import secrets


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _generate_session_id() -> str:
    """Return a short, URL-safe, unique session identifier (16 hex chars)."""
    return secrets.token_hex(8)


# ---------------------------------------------------------------------------
# ChatHistory
# ---------------------------------------------------------------------------

class ChatHistory:
    """
    Persist and recall THEOS conversation sessions.

    Each session is a JSON file on disk::

        <storage_dir>/<session_id>.json

    The JSON schema for a session file::

        {
            "session_id": "...",
            "label": "optional name",
            "created_at": "<ISO-8601 UTC>",
            "updated_at": "<ISO-8601 UTC>",
            "turns": [
                {"role": "user",      "content": "...", "timestamp": "..."},
                {"role": "assistant", "content": "...", "timestamp": "..."},
                ...
            ]
        }

    Args:
        storage_dir: Directory where session files are stored.  Defaults
                     to ``~/.theos/chat_history``.  Created automatically
                     if it does not exist.
    """

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        if storage_dir is None:
            storage_dir = os.path.join(Path.home(), ".theos", "chat_history")
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def new_session(self, label: Optional[str] = None) -> str:
        """
        Create a new, empty chat session and persist it immediately.

        Args:
            label: Human-readable name for the session (optional).

        Returns:
            The new session ID (16-char hex string).
        """
        session_id = _generate_session_id()
        now = _now_iso()
        session = {
            "session_id": session_id,
            "label": label,
            "created_at": now,
            "updated_at": now,
            "turns": [],
        }
        self._write(session_id, session)
        return session_id

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        """
        Append a single turn to an existing session.

        Args:
            session_id: The session to update.
            role: ``"user"`` or ``"assistant"`` (any non-empty string accepted).
            content: The text of the turn.

        Raises:
            ValueError: If *role* or *content* is empty.
            KeyError: If *session_id* does not exist.
        """
        if not role:
            raise ValueError("role must not be empty")
        if not content:
            raise ValueError("content must not be empty")

        session = self._read(session_id)  # raises KeyError if missing
        session["turns"].append({
            "role": role,
            "content": content,
            "timestamp": _now_iso(),
        })
        session["updated_at"] = _now_iso()
        self._write(session_id, session)

    def get_session(self, session_id: str) -> Dict:
        """
        Load a full session by ID.

        Args:
            session_id: The session to retrieve.

        Returns:
            The session dict (``session_id``, ``label``, ``created_at``,
            ``updated_at``, ``turns``).

        Raises:
            KeyError: If *session_id* does not exist.
        """
        return self._read(session_id)

    def get_last_session(self) -> Optional[Dict]:
        """
        Return the most-recently updated session.

        This is the primary way to recall a conversation that has
        "vanished" — i.e. the process was restarted or the window closed.

        Returns:
            The session dict for the most-recently updated session, or
            ``None`` if no sessions have been created yet.
        """
        sessions = self.list_sessions()
        if not sessions:
            return None
        # list_sessions() sorts newest-first by updated_at
        return self.get_session(sessions[0]["session_id"])

    def delete_session(self, session_id: str) -> bool:
        """
        Permanently delete a session.

        Args:
            session_id: The session to delete.

        Returns:
            ``True`` if deleted, ``False`` if not found.
        """
        path = self._path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    # ------------------------------------------------------------------
    # Discovery / search
    # ------------------------------------------------------------------

    def list_sessions(self) -> List[Dict]:
        """
        List metadata for all persisted sessions, newest first.

        Returns:
            List of dicts with keys ``session_id``, ``label``,
            ``created_at``, ``updated_at``, ``turn_count``.
            Raw conversation content is not included.
        """
        results = []
        for path in self._dir.glob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                results.append({
                    "session_id": data.get("session_id", path.stem),
                    "label": data.get("label"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "turn_count": len(data.get("turns", [])),
                })
            except (json.JSONDecodeError, OSError):
                continue  # Skip corrupted files
        results.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
        return results

    def search_sessions(self, keyword: str) -> List[Dict]:
        """
        Search all sessions for a keyword (case-insensitive substring match).

        Searches both the session label and the content of every turn.

        Args:
            keyword: The text to search for.

        Returns:
            List of matching session dicts (full sessions, not just metadata),
            sorted newest first.
        """
        if not keyword:
            return []

        needle = keyword.lower()
        matches = []
        for path in self._dir.glob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                continue

            # Check label
            if data.get("label") and needle in data["label"].lower():
                matches.append(data)
                continue

            # Check turns
            for turn in data.get("turns", []):
                if needle in turn.get("content", "").lower():
                    matches.append(data)
                    break

        matches.sort(key=lambda r: r.get("updated_at") or "", reverse=True)
        return matches

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    #: Characters permitted in a session ID (used both here and in tests).
    _HEX_CHARS = frozenset("0123456789abcdef")

    def _path(self, session_id: str) -> Path:
        """Return the file path for a session."""
        # Sanitise: allow only lowercase hex chars to prevent path traversal
        safe_id = "".join(c for c in session_id.lower() if c in self._HEX_CHARS)
        if not safe_id:
            raise ValueError(f"Invalid session_id: {session_id!r}")
        return self._dir / f"{safe_id}.json"

    def _write(self, session_id: str, data: Dict) -> None:
        """Atomically write session data to disk."""
        path = self._path(session_id)
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        tmp.replace(path)  # atomic on both POSIX and Windows (Python 3.3+)

    def _read(self, session_id: str) -> Dict:
        """Read and return session data from disk."""
        path = self._path(session_id)
        if not path.exists():
            raise KeyError(f"Session not found: {session_id!r}")
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
