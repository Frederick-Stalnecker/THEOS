# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
Unit Tests for THEOS Authentication Token Manager

Validates:
1. Token generation (format, uniqueness, entropy)
2. Token validation (valid, revoked, expired)
3. Token revocation (single, all)
4. Token listing (active only, metadata)
5. Edge cases (unknown tokens, empty store)

Run with:
    pytest tests/test_auth.py -v
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

import pytest
from theos_auth import TokenManager


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def manager():
    """Fresh TokenManager for each test."""
    return TokenManager()


# ==============================================================================
# TOKEN GENERATION
# ==============================================================================

class TestTokenGeneration:
    """Tests for generate_token."""

    def test_returns_string(self, manager):
        token = manager.generate_token()
        assert isinstance(token, str)

    def test_token_is_64_hex_chars(self, manager):
        """Token should be 64 lowercase hex characters (256-bit)."""
        token = manager.generate_token()
        assert len(token) == 64
        assert all(c in "0123456789abcdef" for c in token)

    def test_tokens_are_unique(self, manager):
        tokens = {manager.generate_token() for _ in range(50)}
        assert len(tokens) == 50

    def test_generate_with_label(self, manager):
        token = manager.generate_token(label="ci-pipeline")
        listing = manager.list_tokens()
        assert any(r["label"] == "ci-pipeline" for r in listing)

    def test_generate_without_label(self, manager):
        token = manager.generate_token()
        listing = manager.list_tokens()
        assert listing[0]["label"] is None

    def test_generate_with_ttl(self, manager):
        token = manager.generate_token(ttl_seconds=3600)
        listing = manager.list_tokens()
        assert listing[0]["expires_at"] is not None

    def test_generate_without_ttl_no_expiry(self, manager):
        token = manager.generate_token()
        listing = manager.list_tokens()
        assert listing[0]["expires_at"] is None


# ==============================================================================
# TOKEN VALIDATION
# ==============================================================================

class TestTokenValidation:
    """Tests for validate_token."""

    def test_valid_token_accepted(self, manager):
        token = manager.generate_token()
        assert manager.validate_token(token) is True

    def test_unknown_token_rejected(self, manager):
        assert manager.validate_token("deadbeef" * 8) is False

    def test_empty_string_rejected(self, manager):
        assert manager.validate_token("") is False

    def test_expired_token_rejected(self, manager):
        token = manager.generate_token(ttl_seconds=1)
        time.sleep(1.1)
        assert manager.validate_token(token) is False

    def test_non_expired_token_accepted(self, manager):
        token = manager.generate_token(ttl_seconds=60)
        assert manager.validate_token(token) is True

    def test_validate_multiple_active_tokens(self, manager):
        tokens = [manager.generate_token() for _ in range(5)]
        for t in tokens:
            assert manager.validate_token(t) is True


# ==============================================================================
# TOKEN REVOCATION
# ==============================================================================

class TestTokenRevocation:
    """Tests for revoke_token and revoke_all."""

    def test_revoke_valid_token(self, manager):
        token = manager.generate_token()
        result = manager.revoke_token(token)
        assert result is True

    def test_revoked_token_no_longer_valid(self, manager):
        token = manager.generate_token()
        manager.revoke_token(token)
        assert manager.validate_token(token) is False

    def test_revoke_unknown_token_returns_false(self, manager):
        result = manager.revoke_token("unknown" * 9)
        assert result is False

    def test_revoke_same_token_twice(self, manager):
        token = manager.generate_token()
        assert manager.revoke_token(token) is True
        assert manager.revoke_token(token) is False

    def test_revoke_all_clears_store(self, manager):
        for _ in range(5):
            manager.generate_token()
        count = manager.revoke_all()
        assert count == 5
        assert manager.list_tokens() == []

    def test_revoke_all_empty_store(self, manager):
        assert manager.revoke_all() == 0

    def test_revoke_one_does_not_affect_others(self, manager):
        t1 = manager.generate_token()
        t2 = manager.generate_token()
        manager.revoke_token(t1)
        assert manager.validate_token(t2) is True


# ==============================================================================
# TOKEN LISTING
# ==============================================================================

class TestTokenListing:
    """Tests for list_tokens."""

    def test_list_empty_store(self, manager):
        assert manager.list_tokens() == []

    def test_list_shows_active_tokens(self, manager):
        manager.generate_token(label="a")
        manager.generate_token(label="b")
        listing = manager.list_tokens()
        assert len(listing) == 2

    def test_list_excludes_revoked_tokens(self, manager):
        t1 = manager.generate_token(label="keep")
        t2 = manager.generate_token(label="remove")
        manager.revoke_token(t2)
        listing = manager.list_tokens()
        assert len(listing) == 1
        assert listing[0]["label"] == "keep"

    def test_list_excludes_expired_tokens(self, manager):
        manager.generate_token(label="permanent")
        manager.generate_token(ttl_seconds=1, label="temporary")
        time.sleep(1.1)
        listing = manager.list_tokens()
        assert len(listing) == 1
        assert listing[0]["label"] == "permanent"

    def test_list_does_not_expose_raw_token(self, manager):
        token = manager.generate_token()
        listing = manager.list_tokens()
        for record in listing:
            assert token not in record.values()

    def test_list_record_has_required_keys(self, manager):
        manager.generate_token()
        record = manager.list_tokens()[0]
        assert "created_at" in record
        assert "expires_at" in record
        assert "label" in record
