"""MCP support in the generated client, and the ``channel_type`` rename.

Both come from the same spec refresh, so they're covered together: the enum
members are what let an MCP service be uploaded at all, and the rename is the
one caller-visible break that refresh carried.
"""

import inspect

from unitysvc_sellers._generated.models.access_method_enum import (
    ACCESS_METHOD_ENUM_VALUES,
    check_access_method_enum,
)
from unitysvc_sellers._generated.models.service_type_enum import (
    SERVICE_TYPE_ENUM_VALUES,
    check_service_type_enum,
)
from unitysvc_sellers.aservices import AsyncServices
from unitysvc_sellers.services import Services, _resolve_channel_type


class TestMcpEnumMembers:
    """``mcp`` must survive the client-side ``check_*`` gate.

    These are ``Literal`` sets frozen at generation time, so a stale client
    raises ``TypeError`` before the request leaves the machine — the upload
    never reaches the backend to be judged on its merits.
    """

    def test_service_type_accepts_mcp(self) -> None:
        assert check_service_type_enum("mcp") == "mcp"
        assert "mcp" in SERVICE_TYPE_ENUM_VALUES

    def test_access_method_accepts_mcp(self) -> None:
        # An MCP offering's channel carries ``access_method: mcp``; without
        # this the upload fails one step after the service_type check.
        assert check_access_method_enum("mcp") == "mcp"
        assert "mcp" in ACCESS_METHOD_ENUM_VALUES


class TestCoreDependencyFloor:
    """The generated enums are only half the gate.

    ``specs validate`` runs against unitysvc-core's bundled schema, which is a
    separate package with its own release cadence. A client that accepts
    ``mcp`` paired with a core that doesn't still fails — just one step
    earlier, at validate rather than upload. These assert the *installed*
    core satisfies what the declared floor promises.
    """

    def test_core_service_type_has_mcp(self) -> None:
        from unitysvc_core.models.base import ServiceTypeEnum

        assert hasattr(ServiceTypeEnum, "mcp")

    def test_core_access_method_has_mcp(self) -> None:
        from unitysvc_core.models.base import AccessMethodEnum

        assert hasattr(AccessMethodEnum, "mcp")

    def test_core_ships_the_mcp_offering_validator(self) -> None:
        from unitysvc_core.models.validators import validate_mcp_offering

        assert callable(validate_mcp_offering)


class TestResolveChannelType:
    def test_channel_type_passes_through(self) -> None:
        assert _resolve_channel_type("managed", None) == "managed"

    def test_listing_type_is_accepted_as_the_old_name(self) -> None:
        assert _resolve_channel_type(None, "byok") == "byok"

    def test_channel_type_wins_when_both_given(self) -> None:
        assert _resolve_channel_type("byoe", "byok") == "byoe"

    def test_neither_given_is_no_filter(self) -> None:
        assert _resolve_channel_type(None, None) is None


class TestListSignatures:
    """The rename is additive on the public surface, in sync and async alike."""

    def test_sync_list_accepts_both_names(self) -> None:
        params = inspect.signature(Services.list).parameters
        assert "channel_type" in params
        assert "listing_type" in params

    def test_async_list_accepts_both_names(self) -> None:
        params = inspect.signature(AsyncServices.list).parameters
        assert "channel_type" in params
        assert "listing_type" in params

    def test_iter_all_accepts_both_names(self) -> None:
        for method in (Services.iter_all, AsyncServices.iter_all):
            params = inspect.signature(method).parameters
            assert "channel_type" in params, method
            assert "listing_type" in params, method
