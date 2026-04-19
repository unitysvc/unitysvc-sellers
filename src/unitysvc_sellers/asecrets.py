"""Async mirror of :mod:`secrets`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.secret_public import SecretPublic
    from ._generated.models.secrets_public import SecretsPublic


class AsyncSecrets:
    """Async operations on the seller's secrets."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def list(self, *, skip: int = 0, limit: int = 100) -> SecretsPublic:
        """List the seller's secrets (metadata only)."""
        from ._generated.api.seller_secrets import seller_secrets_list_secrets

        return unwrap(
            await seller_secrets_list_secrets.asyncio_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    async def get(self, name: str) -> SecretPublic:
        """Get metadata for a single secret by name."""
        from ._generated.api.seller_secrets import seller_secrets_get_secret

        return unwrap(
            await seller_secrets_get_secret.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )

    async def set(self, name: str, value: str) -> SecretPublic:
        """Set ``name`` to ``value`` (idempotent — creates or replaces).

        See :class:`unitysvc_sellers.secrets.Secrets.set`.
        """
        from ._generated.api.seller_secrets import seller_secrets_set_secret
        from ._generated.models.secret_update import SecretUpdate

        return unwrap(
            await seller_secrets_set_secret.asyncio_detailed(
                name=name,
                client=self._client,
                body=SecretUpdate(value=value),
            )
        )

    async def delete(self, name: str) -> None:
        """Delete a secret by name. This action cannot be undone."""
        from ._generated.api.seller_secrets import seller_secrets_delete_secret

        unwrap(
            await seller_secrets_delete_secret.asyncio_detailed(
                name=name,
                client=self._client,
            )
        )
