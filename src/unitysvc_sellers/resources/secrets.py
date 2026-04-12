"""``client.secrets`` — seller secret management.

Wraps the seller-tagged ``/v1/seller/secrets/*`` operations.
Secret values are write-only — only metadata is ever returned.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from .._http import unwrap

if TYPE_CHECKING:
    from .._generated.client import AuthenticatedClient
    from .._generated.models.secret_exists_response import SecretExistsResponse
    from .._generated.models.secret_public import SecretPublic
    from .._generated.models.secrets_public import SecretsPublic


class SecretsResource:
    """Operations on the seller's secrets (``/v1/seller/secrets``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(self, *, skip: int = 0, limit: int = 100) -> SecretsPublic:
        """List the seller's secrets (metadata only — values are never returned)."""
        from .._generated.api.seller_secrets import seller_secrets_list_secrets

        return unwrap(
            seller_secrets_list_secrets.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    def get(self, secret_id: str | UUID) -> SecretPublic:
        """Get metadata for a single secret by id."""
        from .._generated.api.seller_secrets import seller_secrets_get_secret

        return unwrap(
            seller_secrets_get_secret.sync_detailed(
                secret_id=UUID(str(secret_id)),
                client=self._client,
            )
        )

    def create(self, name: str, value: str) -> SecretPublic:
        """Create a new secret. The value cannot be retrieved after creation."""
        from .._generated.api.seller_secrets import seller_secrets_create_secret
        from .._generated.models.secret_create import SecretCreate

        return unwrap(
            seller_secrets_create_secret.sync_detailed(
                client=self._client,
                body=SecretCreate(name=name, value=value),
            )
        )

    def check(self, name: str) -> SecretExistsResponse:
        """Check whether a secret with the given name exists."""
        from .._generated.api.seller_secrets import seller_secrets_check_secret_exists

        return unwrap(
            seller_secrets_check_secret_exists.sync_detailed(
                name=name,
                client=self._client,
            )
        )

    def rotate(self, secret_id: str | UUID, value: str) -> SecretPublic:
        """Rotate (update) the value of an existing secret."""
        from .._generated.api.seller_secrets import seller_secrets_update_secret
        from .._generated.models.secret_update import SecretUpdate

        return unwrap(
            seller_secrets_update_secret.sync_detailed(
                secret_id=UUID(str(secret_id)),
                client=self._client,
                body=SecretUpdate(value=value),
            )
        )

    def delete(self, secret_id: str | UUID) -> None:
        """Delete a secret. This action cannot be undone."""
        from .._generated.api.seller_secrets import seller_secrets_delete_secret

        unwrap(
            seller_secrets_delete_secret.sync_detailed(
                secret_id=UUID(str(secret_id)),
                client=self._client,
            )
        )
