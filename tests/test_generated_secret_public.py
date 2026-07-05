"""Regression tests for generated secret metadata models."""

from __future__ import annotations

from uuid import UUID

from unitysvc_sellers._generated.models.secret_public import SecretPublic


def test_secret_public_accepts_shared_secret_null_owner_id() -> None:
    role_id = "11111111-1111-1111-1111-111111111111"

    secret = SecretPublic.from_dict(
        {
            "name": "API_KEY",
            "id": "22222222-2222-2222-2222-222222222222",
            "owner_type": "seller",
            "role_id": role_id,
            "owner_id": None,
            "created_at": "2026-07-05T12:00:00Z",
            "updated_at": None,
            "last_used_at": None,
        }
    )

    assert secret.owner_type == "seller"
    assert secret.role_id == UUID(role_id)
    assert secret.owner_id is None
    assert secret.to_dict()["owner_id"] is None
