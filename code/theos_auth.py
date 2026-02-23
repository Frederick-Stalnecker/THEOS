# Copyright (c) 2026 Frederick Stalnecker
# Licensed under the MIT License - see LICENSE file for details

"""
THEOS Authentication Token Manager
====================================

Provides secure token-based authentication for THEOS API access.

Key Features:
1. Token Generation: Cryptographically secure random tokens
2. Token Validation: Check token existence and optional expiry
3. Token Revocation: Remove specific or all tokens
4. Token Listing: Enumerate active tokens with metadata

Uses Python standard library only (no external dependencies).

Author: Frederick Davis Stalnecker
"""

import secrets
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone


@dataclass
class TokenRecord:
    """Record of an issued authentication token."""
    token_hash: str          # SHA-256 hash of the raw token (never store raw)
    created_at: datetime
    expires_at: Optional[datetime]  # None means no expiry
    label: Optional[str]     # Optional human-readable label


class TokenManager:
    """
    Manages authentication tokens for THEOS API access.

    Tokens are generated using cryptographically secure random bytes.
    Only the SHA-256 hash of each token is stored internally; the raw
    token is returned once at generation time and never persisted.

    Usage::

        manager = TokenManager()
        token = manager.generate_token(label="my-service")
        # share ``token`` with the caller; store nothing else

        ok = manager.validate_token(token)  # True while active
        manager.revoke_token(token)
        ok = manager.validate_token(token)  # False after revocation
    """

    def __init__(self) -> None:
        # Maps token_hash -> TokenRecord
        self._store: Dict[str, TokenRecord] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_token(
        self,
        ttl_seconds: Optional[int] = None,
        label: Optional[str] = None,
    ) -> str:
        """
        Generate a new cryptographically secure authentication token.

        Args:
            ttl_seconds: Optional time-to-live in seconds.  If given the
                         token automatically becomes invalid after this
                         many seconds.  ``None`` (default) means the token
                         never expires on its own.
            label: Optional human-readable description stored alongside
                   the token record (e.g. ``"ci-pipeline"``).

        Returns:
            A 64-character hex token string.  Show this to the caller
            exactly once; it is not stored in plaintext internally.
        """
        raw_token = secrets.token_hex(32)  # 256 bits of entropy
        token_hash = self._hash(raw_token)

        now = datetime.now(timezone.utc)
        expires_at: Optional[datetime] = None
        if ttl_seconds is not None:
            expires_at = now + timedelta(seconds=ttl_seconds)

        self._store[token_hash] = TokenRecord(
            token_hash=token_hash,
            created_at=now,
            expires_at=expires_at,
            label=label,
        )
        return raw_token

    def validate_token(self, token: str) -> bool:
        """
        Check whether *token* is valid and not expired.

        Args:
            token: The raw token string returned by :meth:`generate_token`.

        Returns:
            ``True`` if the token exists and has not expired, ``False``
            otherwise.
        """
        token_hash = self._hash(token)
        record = self._store.get(token_hash)
        if record is None:
            return False
        if record.expires_at is not None and datetime.now(timezone.utc) > record.expires_at:
            # Lazily clean up expired token
            del self._store[token_hash]
            return False
        return True

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a previously issued token.

        Args:
            token: The raw token string to revoke.

        Returns:
            ``True`` if the token was found and revoked, ``False`` if it
            was not present (already revoked or never issued).
        """
        token_hash = self._hash(token)
        if token_hash in self._store:
            del self._store[token_hash]
            return True
        return False

    def list_tokens(self) -> List[Dict]:
        """
        List all active (non-expired) token records.

        The raw token values are **never** included in the listing; only
        metadata such as creation time, expiry, and label are returned.

        Returns:
            A list of dicts, each containing:
            ``created_at``, ``expires_at``, and ``label`` keys.
        """
        now = datetime.now(timezone.utc)
        result = []
        expired_hashes = []
        for token_hash, record in self._store.items():
            if record.expires_at is not None and now > record.expires_at:
                expired_hashes.append(token_hash)
                continue
            result.append({
                "created_at": record.created_at.isoformat(),
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
                "label": record.label,
            })
        for h in expired_hashes:
            del self._store[h]
        return result

    def revoke_all(self) -> int:
        """
        Revoke every token currently held by this manager.

        Returns:
            Number of tokens revoked.
        """
        count = len(self._store)
        self._store.clear()
        return count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash(token: str) -> str:
        """Return the SHA-256 hex digest of *token*."""
        return hashlib.sha256(token.encode()).hexdigest()
