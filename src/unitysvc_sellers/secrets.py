"""``client.secrets`` — seller secret management.

Wraps the seller-tagged ``/v1/seller/secrets/*`` operations.
Secret values are write-only — only metadata is ever returned.

API shape mirrors GitHub's secrets API (see unitysvc/unitysvc#798):

* :meth:`list`   — ``GET /``
* :meth:`get`    — ``GET /{name}``  (metadata only)
* :meth:`set`    — ``PUT /{name}``  (idempotent create-or-replace)
* :meth:`delete` — ``DELETE /{name}``

There is no separate ``create`` or ``rotate`` method — :meth:`set`
does both create and rotate in one idempotent call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.secret_public import SecretPublic
    from ._generated.models.secrets_public import SecretsPublic


class Secrets:
    """Operations on the seller's secrets (``/v1/seller/secrets``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(self, *, skip: int = 0, limit: int = 100) -> SecretsPublic:
        """List the seller's secrets (metadata only — values are never returned)."""
        from ._generated.api.seller_secrets import seller_secrets_list_secrets

        return unwrap(
            seller_secrets_list_secrets.sync_detailed(
                client=self._client,
                skip=skip,
                limit=limit,
            )
        )

    def get(self, name: str) -> SecretPublic:
        """Get metadata for a single secret by name."""
        from ._generated.api.seller_secrets import seller_secrets_get_secret

        return unwrap(
            seller_secrets_get_secret.sync_detailed(
                name=name,
                client=self._client,
            )
        )

    def set(self, name: str, value: str) -> SecretPublic:
        """Set ``name`` to ``value`` (idempotent — creates or replaces).

        Maps to ``PUT /v1/seller/secrets/{name}``. Returns the secret's
        public metadata; the value itself is never echoed back.
        """
        from ._generated.api.seller_secrets import seller_secrets_set_secret
        from ._generated.models.secret_update import SecretUpdate

        return unwrap(
            seller_secrets_set_secret.sync_detailed(
                name=name,
                client=self._client,
                body=SecretUpdate(value=value),
            )
        )

    def delete(self, name: str) -> None:
        """Delete a secret by name. This action cannot be undone."""
        from ._generated.api.seller_secrets import seller_secrets_delete_secret

        unwrap(
            seller_secrets_delete_secret.sync_detailed(
                name=name,
                client=self._client,
            )
        )
