"""
Tests for the THEOS MCP Lab Assistant Server
=============================================

Validates every tool exposed by theos_mcp_server without starting an actual
MCP transport — we call the internal handler helpers directly.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

# ---------------------------------------------------------------------------
# Load the MCP server module
# ---------------------------------------------------------------------------
_CODE_DIR = Path(__file__).resolve().parent.parent / "code"
sys.path.insert(0, str(_CODE_DIR))

_spec = importlib.util.spec_from_file_location(
    "theos_mcp_server", str(_CODE_DIR / "theos_mcp_server.py")
)
_mcp_mod: ModuleType = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mcp_mod)  # type: ignore[union-attr]


# ── Helpers ────────────────────────────────────────────────────────────────

def _text(results) -> str:
    """Extract the plain text from a list[TextContent]."""
    return "\n".join(r.text for r in results)


# ---------------------------------------------------------------------------
# list_tools
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_tools_returns_six_tools():
    tools = await _mcp_mod.list_tools()
    names = {t.name for t in tools}
    assert names == {
        "list_repository_files",
        "read_repository_file",
        "launch_theos_demo",
        "run_theos_query",
        "get_theos_status",
        "run_tests",
    }


# ---------------------------------------------------------------------------
# list_repository_files
# ---------------------------------------------------------------------------

def test_list_repository_files_root():
    results = _mcp_mod._list_repository_files(".")
    text = _text(results)
    assert "code" in text
    assert "tests" in text


def test_list_repository_files_code_dir():
    results = _mcp_mod._list_repository_files("code")
    text = _text(results)
    assert "theos_core.py" in text or "theos_mcp_server.py" in text


def test_list_repository_files_missing_path():
    results = _mcp_mod._list_repository_files("nonexistent_dir_xyz")
    assert "not found" in _text(results).lower()


def test_list_repository_files_path_traversal_blocked():
    results = _mcp_mod._list_repository_files("../../etc")
    assert "outside the repository" in _text(results).lower()


# ---------------------------------------------------------------------------
# read_repository_file
# ---------------------------------------------------------------------------

def test_read_repository_file_readme():
    results = _mcp_mod._read_repository_file("README.md")
    text = _text(results)
    assert "THEOS" in text


def test_read_repository_file_code():
    results = _mcp_mod._read_repository_file("code/theos_core.py")
    text = _text(results)
    assert "TheosCore" in text


def test_read_repository_file_missing():
    results = _mcp_mod._read_repository_file("does_not_exist.xyz")
    assert "not found" in _text(results).lower()


def test_read_repository_file_path_traversal_blocked():
    results = _mcp_mod._read_repository_file("../../etc/passwd")
    assert "outside the repository" in _text(results).lower()


# ---------------------------------------------------------------------------
# launch_theos_demo
# ---------------------------------------------------------------------------

def test_launch_theos_demo_default():
    results = _mcp_mod._launch_theos_demo(None)
    text = _text(results)
    # The demo prints a separator line and a "Prompt:" line
    assert "THEOS" in text or "Cycle" in text or "Governor" in text


def test_launch_theos_demo_custom_prompt():
    results = _mcp_mod._launch_theos_demo("What is contradiction-bounded reasoning?")
    text = _text(results)
    assert len(text) > 0


# ---------------------------------------------------------------------------
# run_theos_query
# ---------------------------------------------------------------------------

def test_run_theos_query_basic():
    results = _mcp_mod._run_theos_query(
        "How does THEOS bound contradiction?",
        "Contradiction is bounded by a finite budget that decreases each cycle.",
        "Contradiction may not converge if the engines are misaligned.",
    )
    data = json.loads(_text(results))
    assert data["query"] == "How does THEOS bound contradiction?"
    assert "chosen_answer" in data
    assert "cycles_run" in data
    assert data["cycles_run"] >= 1


def test_run_theos_query_no_reasoning_supplied():
    """If no reasoning is provided the server generates default text."""
    results = _mcp_mod._run_theos_query("Minimal query", "", "")
    data = json.loads(_text(results))
    assert "chosen_engine" in data
    assert data["chosen_engine"] in ("L", "R", "N/A")


def test_run_theos_query_returns_json():
    results = _mcp_mod._run_theos_query("JSON test", "", "")
    # Must be valid JSON
    data = json.loads(_text(results))
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# get_theos_status
# ---------------------------------------------------------------------------

def test_get_theos_status_structure():
    results = _mcp_mod._get_theos_status()
    data = json.loads(_text(results))
    assert "governor_config" in data
    assert "governor_state" in data
    assert "theos_core" in data
    assert "repository_root" in data


def test_get_theos_status_governor_config_values():
    results = _mcp_mod._get_theos_status()
    data = json.loads(_text(results))
    cfg = data["governor_config"]
    assert cfg["max_cycles"] == 5
    assert cfg["contradiction_budget"] == 1.5


# ---------------------------------------------------------------------------
# run_tests
# ---------------------------------------------------------------------------

def test_run_tests_specific_file():
    """Run just the fast governor tests to keep this test quick."""
    results = _mcp_mod._run_tests("tests/test_governor.py")
    text = _text(results)
    assert "passed" in text.lower()


def test_run_tests_missing_file():
    results = _mcp_mod._run_tests("tests/nonexistent_test_xyz.py")
    text = _text(results)
    # pytest will report an error for missing path
    assert len(text) > 0
