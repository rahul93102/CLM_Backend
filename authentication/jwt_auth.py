"""Stateless JWT auth (no DB lookup per request).

We still use SimpleJWT tokens, but we avoid the default `JWTAuthentication.get_user()`
DB query that fails hard when Supabase/Postgres is temporarily unavailable.

This keeps Supabase as the only DB while making authentication resilient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from rest_framework_simplejwt.authentication import JWTAuthentication


@dataclass
class JWTClaimsUser:
    """Lightweight authenticated user built from JWT claims."""

    user_id: str
    email: Optional[str] = None
    tenant_id: Optional[str] = None
    is_admin: bool = False
    is_superadmin: bool = False

    is_authenticated: bool = True
    is_anonymous: bool = False

    @property
    def pk(self) -> str:
        return self.user_id

    def __str__(self) -> str:
        return self.email or self.user_id


class StatelessJWTAuthentication(JWTAuthentication):
    """Same validation as SimpleJWT, but no database user fetch."""

    def get_user(self, validated_token):  # type: ignore[override]
        user_id = str(validated_token.get("user_id") or validated_token.get("sub") or "")
        if not user_id:
            # Let upstream error handling deal with malformed tokens.
            user_id = ""

        return JWTClaimsUser(
            user_id=user_id,
            email=validated_token.get("email"),
            tenant_id=validated_token.get("tenant_id"),
            is_admin=bool(validated_token.get("is_admin") or validated_token.get("role") == "admin"),
            is_superadmin=bool(validated_token.get("is_superadmin") or validated_token.get("role") == "superadmin"),
        )
