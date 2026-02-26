# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
Unit Tests for THEOS Chat History

Validates:
1. Session creation and persistence
2. Turn recording (user / assistant)
3. Last-session recall (the core "it just vanished" use-case)
4. Session listing (sorted newest-first, metadata only)
5. Keyword search across sessions
6. Session deletion
7. Edge cases (empty keyword, unknown IDs, invalid role/content)

Run with:
    pytest tests/test_chat_history.py -v
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

import pytest
from theos_chat_history import ChatHistory


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def history(tmp_path):
    """Fresh ChatHistory backed by a temporary directory."""
    return ChatHistory(storage_dir=str(tmp_path))


# ==============================================================================
# SESSION CREATION
# ==============================================================================

class TestNewSession:
    """Tests for new_session."""

    def test_returns_string_id(self, history):
        sid = history.new_session()
        assert isinstance(sid, str)

    def test_id_is_16_hex_chars(self, history):
        sid = history.new_session()
        assert len(sid) == 16
        assert all(c in "0123456789abcdef" for c in sid)

    def test_ids_are_unique(self, history):
        ids = {history.new_session() for _ in range(20)}
        assert len(ids) == 20

    def test_session_stored_immediately(self, history):
        sid = history.new_session(label="test-session")
        session = history.get_session(sid)
        assert session["session_id"] == sid

    def test_label_persisted(self, history):
        sid = history.new_session(label="my-project")
        session = history.get_session(sid)
        assert session["label"] == "my-project"

    def test_no_label_stored_as_none(self, history):
        sid = history.new_session()
        session = history.get_session(sid)
        assert session["label"] is None

    def test_new_session_has_empty_turns(self, history):
        sid = history.new_session()
        session = history.get_session(sid)
        assert session["turns"] == []


# ==============================================================================
# TURN RECORDING
# ==============================================================================

class TestAddTurn:
    """Tests for add_turn."""

    def test_add_user_turn(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "Hello!")
        session = history.get_session(sid)
        assert len(session["turns"]) == 1
        assert session["turns"][0]["role"] == "user"
        assert session["turns"][0]["content"] == "Hello!"

    def test_add_assistant_turn(self, history):
        sid = history.new_session()
        history.add_turn(sid, "assistant", "Hi there!")
        session = history.get_session(sid)
        assert session["turns"][0]["role"] == "assistant"

    def test_multiple_turns_ordered(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "First")
        history.add_turn(sid, "assistant", "Second")
        history.add_turn(sid, "user", "Third")
        turns = history.get_session(sid)["turns"]
        assert [t["content"] for t in turns] == ["First", "Second", "Third"]

    def test_turn_has_timestamp(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "test")
        turn = history.get_session(sid)["turns"][0]
        assert "timestamp" in turn
        assert turn["timestamp"]

    def test_updated_at_changes_after_turn(self, history):
        sid = history.new_session()
        created = history.get_session(sid)["updated_at"]
        time.sleep(0.01)
        history.add_turn(sid, "user", "msg")
        updated = history.get_session(sid)["updated_at"]
        assert updated >= created

    def test_empty_role_raises(self, history):
        sid = history.new_session()
        with pytest.raises(ValueError):
            history.add_turn(sid, "", "content")

    def test_empty_content_raises(self, history):
        sid = history.new_session()
        with pytest.raises(ValueError):
            history.add_turn(sid, "user", "")

    def test_unknown_session_raises(self, history):
        with pytest.raises(KeyError):
            history.add_turn("deadbeefdeadbeef", "user", "hello")


# ==============================================================================
# GET LAST SESSION (core recall feature)
# ==============================================================================

class TestGetLastSession:
    """Tests for get_last_session."""

    def test_returns_none_when_empty(self, history):
        assert history.get_last_session() is None

    def test_returns_only_session(self, history):
        sid = history.new_session(label="only")
        result = history.get_last_session()
        assert result["session_id"] == sid

    def test_returns_most_recently_updated(self, history):
        sid_a = history.new_session(label="older")
        time.sleep(0.02)
        sid_b = history.new_session(label="newer")
        result = history.get_last_session()
        assert result["session_id"] == sid_b

    def test_turns_updated_promotes_session(self, history):
        sid_a = history.new_session(label="a")
        time.sleep(0.02)
        sid_b = history.new_session(label="b")
        # Now update session A — it should become the most recent
        time.sleep(0.02)
        history.add_turn(sid_a, "user", "late message")
        result = history.get_last_session()
        assert result["session_id"] == sid_a

    def test_last_session_includes_turns(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "Remember me!")
        result = history.get_last_session()
        assert result["turns"][0]["content"] == "Remember me!"

    def test_survives_new_history_instance(self, tmp_path):
        """Simulates process restart: new ChatHistory, same storage dir."""
        h1 = ChatHistory(storage_dir=str(tmp_path))
        sid = h1.new_session(label="important chat")
        h1.add_turn(sid, "user", "What is THEOS?")
        h1.add_turn(sid, "assistant", "A dual-engine reasoning framework.")

        # Simulate restart
        h2 = ChatHistory(storage_dir=str(tmp_path))
        recalled = h2.get_last_session()

        assert recalled["session_id"] == sid
        assert recalled["turns"][1]["content"] == "A dual-engine reasoning framework."


# ==============================================================================
# SESSION LISTING
# ==============================================================================

class TestListSessions:
    """Tests for list_sessions."""

    def test_empty_store(self, history):
        assert history.list_sessions() == []

    def test_lists_all_sessions(self, history):
        history.new_session()
        history.new_session()
        assert len(history.list_sessions()) == 2

    def test_sorted_newest_first(self, history):
        sid_a = history.new_session(label="first")
        time.sleep(0.02)
        sid_b = history.new_session(label="second")
        listing = history.list_sessions()
        assert listing[0]["session_id"] == sid_b
        assert listing[1]["session_id"] == sid_a

    def test_listing_contains_metadata_keys(self, history):
        history.new_session(label="check")
        record = history.list_sessions()[0]
        for key in ("session_id", "label", "created_at", "updated_at", "turn_count"):
            assert key in record

    def test_turn_count_is_accurate(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "a")
        history.add_turn(sid, "assistant", "b")
        record = history.list_sessions()[0]
        assert record["turn_count"] == 2

    def test_listing_does_not_include_turn_content(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "secret message")
        record = history.list_sessions()[0]
        assert "turns" not in record
        assert "secret message" not in str(record)


# ==============================================================================
# SEARCH
# ==============================================================================

class TestSearchSessions:
    """Tests for search_sessions."""

    def test_empty_keyword_returns_empty(self, history):
        history.new_session()
        assert history.search_sessions("") == []

    def test_match_in_turn_content(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "What is THEOS?")
        results = history.search_sessions("THEOS")
        assert any(r["session_id"] == sid for r in results)

    def test_case_insensitive_match(self, history):
        sid = history.new_session()
        history.add_turn(sid, "user", "Dual-Engine reasoning")
        assert any(r["session_id"] == sid for r in history.search_sessions("dual-engine"))
        assert any(r["session_id"] == sid for r in history.search_sessions("DUAL-ENGINE"))

    def test_match_in_label(self, history):
        sid = history.new_session(label="finance-project")
        results = history.search_sessions("finance")
        assert any(r["session_id"] == sid for r in results)

    def test_no_match_returns_empty(self, history):
        history.new_session()
        assert history.search_sessions("xyzzy-notpresent") == []

    def test_multiple_sessions_only_matching_returned(self, history):
        sid_a = history.new_session(label="alpha")
        sid_b = history.new_session(label="beta")
        history.add_turn(sid_a, "user", "needle in haystack")
        results = history.search_sessions("needle")
        ids = [r["session_id"] for r in results]
        assert sid_a in ids
        assert sid_b not in ids


# ==============================================================================
# SESSION DELETION
# ==============================================================================

class TestDeleteSession:
    """Tests for delete_session."""

    def test_delete_existing_returns_true(self, history):
        sid = history.new_session()
        assert history.delete_session(sid) is True

    def test_deleted_session_not_in_listing(self, history):
        sid = history.new_session()
        history.delete_session(sid)
        ids = [r["session_id"] for r in history.list_sessions()]
        assert sid not in ids

    def test_delete_non_existent_returns_false(self, history):
        assert history.delete_session("deadbeefdeadbeef") is False

    def test_get_session_raises_after_delete(self, history):
        sid = history.new_session()
        history.delete_session(sid)
        with pytest.raises(KeyError):
            history.get_session(sid)
