"""Regression tests for generated service group metadata models."""

from __future__ import annotations

from uuid import UUID

from unitysvc_sellers._generated.models.service_group_public import ServiceGroupPublic


def test_service_group_public_accepts_shared_group_null_owner_id() -> None:
    role_id = "11111111-1111-1111-1111-111111111111"

    group = ServiceGroupPublic.from_dict(
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "role_id": role_id,
            "owner_id": None,
            "owner_type": "seller",
            "name": "group",
            "display_name": "group",
            "status": "active",
            "created_at": "2026-07-05T12:00:00Z",
        }
    )

    assert group.owner_type == "seller"
    assert group.role_id == UUID(role_id)
    assert group.owner_id is None
    assert group.to_dict()["owner_id"] is None


def test_service_group_public_omits_owner_id_when_absent() -> None:
    role_id = "33333333-3333-3333-3333-333333333333"

    group = ServiceGroupPublic.from_dict(
        {
            "id": "44444444-4444-4444-4444-444444444444",
            "role_id": role_id,
            "owner_type": "seller",
            "name": "group",
            "display_name": "group",
            "status": "active",
            "created_at": "2026-07-05T12:00:00Z",
        }
    )

    assert group.role_id == UUID(role_id)
    assert "owner_id" not in group.to_dict()
