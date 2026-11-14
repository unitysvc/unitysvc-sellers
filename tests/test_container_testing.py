from pathlib import Path
from typing import Any

import pytest
import respx
from httpx import Response
from unitysvc_core.models.channel import ContainerChannel
from unitysvc_core.models.probes import ProbesV1

from unitysvc_sellers import container_testing as runner

IMAGE = "example/app@sha256:" + "a" * 64
SOURCE = f"""services:
  web:
    image: {IMAGE}
    ports: [8080]
    environment:
      API_KEY: ${{UNITYSVC_INSTANCE_API_KEY}}
"""


def channel() -> ContainerChannel:
    return ContainerChannel.model_validate(
        {
            "access_method": "container",
            "spec": "Application",
            "resources": {"limits": {"cpu": "250m", "memory": "256Mi", "ephemeral-storage": "1Gi"}},
            "entries": [{"name": "web", "service": "web", "port": 8080, "auth": "app"}],
            "customer_access_requests": [{"object": "resource:container", "permissions": ["create"], "required": True}],
        }
    )


def test_rejects_unsafe_spec_before_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setattr(runner, "_docker", lambda *a, **kw: calls.append(a))
    with pytest.raises(ValueError, match="privileged"):
        runner.test_container(SOURCE + "    privileged: true\n", channel())
    assert not calls


def test_does_not_import_host_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setenv("SELLER_SECRET", "host-secret-must-stay-on-host")
    monkeypatch.setattr(runner, "_docker", lambda *a, **kw: calls.append(a))
    with pytest.raises(RuntimeError, match="resolved"):
        runner.test_container(SOURCE.replace("UNITYSVC_INSTANCE_API_KEY", "SELLER_SECRET"), channel())
    assert not calls


@pytest.mark.parametrize("status", [200, 503])
def test_probes_use_fresh_app_key_and_cleanup_even_on_failure(monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    calls: list[tuple[str, ...]] = []
    generated: list[str] = []

    def docker(*args: str, **kwargs: Any) -> str:
        calls.append(args)
        if args[0] == "run":
            env_path = Path(args[args.index("--env-file") + 1])
            generated.append(env_path.read_text().removeprefix("API_KEY=").strip())
            assert env_path.stat().st_mode & 0o777 == 0o600
            assert "--cap-drop" in args
        return "127.0.0.1:54321" if args[0] == "port" else ""

    monkeypatch.setattr(runner, "_docker", docker)
    monkeypatch.setattr(runner, "_ready", lambda *args: True)
    monkeypatch.setenv("UNITYSVC_INSTANCE_API_KEY", "a-host-key-that-must-not-be-reused")
    with respx.mock() as mock:
        route = mock.get("http://127.0.0.1:54321/").mock(return_value=Response(status))
        if status == 200:
            assert runner.test_container(SOURCE, channel())[-1] == "web/: HTTP 200"
        else:
            with pytest.raises(RuntimeError, match="HTTP 503"):
                runner.test_container(SOURCE, channel())
        assert route.calls[0].request.headers["Authorization"] == f"Bearer {generated[0]}"
    assert len(generated[0]) >= 32
    assert generated[0] != "a-host-key-that-must-not-be-reused"
    assert any(args[0] == "rm" for args in calls)
    assert calls[-1][:2] == ("network", "rm")


def test_unknown_probe_entry_is_rejected_before_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setattr(runner, "_docker", lambda *a, **kw: calls.append(a))
    probes = ProbesV1(probes=[{"entry": "other"}])
    with pytest.raises(ValueError, match="entry missing"):
        runner.test_container(SOURCE, channel(), probes)
    assert not calls
