"""``services.get()`` must return a parsed model, not a raw dict.

Regression cover for unitysvc/unitysvc-sellers#205. ``ServiceDetailResponse``
stopped being generated at 0.3.7 — two schemas collided on one class name, the
generator dropped one and silently removed everything referencing it — so
``services_get._parse_response`` had no 200 branch at all. ``Services.get``
falls back to the raw body when ``parsed`` is None, so nothing failed at the
call; callers broke later on the first nested attribute access
(``'dict' object has no attribute 'category'``).

Two tests, for the two halves of the failure:

* one drives ``services.get()`` over a mocked backend and pins the typed
  result, so the 200 branch cannot vanish again unnoticed;
* one checks **every** generated operation for the same silent drop, since the
  next model to trip the same generator behaviour will not be this one.
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import uuid

import httpx
import pytest
import respx

from unitysvc_sellers import Client

BASE_URL = "https://seller.test.unitysvc"

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_API_DIR = _REPO_ROOT / "src" / "unitysvc_sellers" / "_generated" / "api"
_SPEC = json.loads((_REPO_ROOT / "openapi.json").read_text())


@pytest.fixture
def client() -> Client:
    return Client(api_key="svcpass_test_key", base_url=BASE_URL)


def _detail_payload(service_id: str) -> dict:
    return {
        "service_id": service_id,
        "service_name": "fireworks/llama-v3",
        "status": "active",
        "documents": [
            {
                "id": str(uuid.uuid4()),
                "title": "Getting started",
                "category": "getting_started",
            }
        ],
        "interfaces": [],
    }


@respx.mock
def test_get_returns_a_parsed_model(client: Client) -> None:
    service_id = str(uuid.uuid4())
    respx.get(f"{BASE_URL}/services/{service_id}").mock(
        return_value=httpx.Response(200, json=_detail_payload(service_id))
    )

    # Imported here, not at module scope: if this model is dropped again the
    # failure should land on this test, not on collecting the file, so the
    # cross-operation audit below still runs and reports.
    from unitysvc_sellers._generated.models import ServiceDetailResponse

    service = client.services.get(service_id)

    # The wrapper accepts either a model or a dict, so assert on what it is
    # holding — a dict here is the bug, and it is invisible from the outside.
    raw = object.__getattribute__(service, "_raw")
    assert isinstance(raw, ServiceDetailResponse), f"expected a parsed model, got {type(raw).__name__}"


@respx.mock
def test_nested_fields_support_attribute_access(client: Client) -> None:
    """The symptom callers actually hit: ``.documents[0].category``."""
    service_id = str(uuid.uuid4())
    respx.get(f"{BASE_URL}/services/{service_id}").mock(
        return_value=httpx.Response(200, json=_detail_payload(service_id))
    )

    service = client.services.get(service_id)

    assert service.service_id == service_id
    assert service.documents[0].category == "getting_started"
    assert service.documents[0].title == "Getting started"


@respx.mock
def test_unparseable_success_body_raises_a_typed_error(client: Client) -> None:
    """A 200 the SDK cannot decode must not leak the generator's KeyError.

    ``from_dict`` pops required keys, so a body that does not match the declared
    schema raises ``KeyError`` from inside the generated layer. Callers catch
    ``SellerSDKError``; the CLI's partial-id resolver relies on that to fall
    through to its list-and-prefix-match path instead of aborting.
    """
    from unitysvc_sellers.exceptions import ResponseParseError, SellerSDKError

    service_id = str(uuid.uuid4())
    respx.get(f"{BASE_URL}/services/{service_id}").mock(
        # A ServicePublic-shaped body: keys the id as `id`, not `service_id`.
        return_value=httpx.Response(200, json={"id": service_id, "status": "active"})
    )

    with pytest.raises(ResponseParseError) as excinfo:
        client.services.get(service_id)

    assert isinstance(excinfo.value, SellerSDKError)
    assert excinfo.value.status_code == 200
    assert isinstance(excinfo.value.__cause__, KeyError)


def _success_branches(parse_response: ast.FunctionDef) -> set[int]:
    """Status codes the generated ``_parse_response`` handles, 2xx only."""
    handled = set()
    for node in ast.walk(parse_response):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.left, ast.Attribute)
            and test.left.attr == "status_code"
            and isinstance(test.comparators[0], ast.Constant)
            and isinstance(test.comparators[0].value, int)
        ):
            handled.add(test.comparators[0].value)
    return {code for code in handled if 200 <= code < 300}


def _spec_success_body(method: str, path: str) -> str | None:
    """The 2xx response schema the spec declares, if it has a JSON body."""
    operation = _SPEC.get("paths", {}).get(path, {}).get(method, {})
    for code, response in operation.get("responses", {}).items():
        if not code.startswith("2"):
            continue
        schema = response.get("content", {}).get("application/json", {}).get("schema")
        return json.dumps(schema) if schema else None
    return None


# ``_get_kwargs`` builds the request dict with literal keys, e.g.
#     "method": "get",
#     "url": "/services/{service_id}".format(...)
# Matched on the source rather than the parsed tree: ``ast.unparse`` collapses
# the dict onto one line, which makes a line-oriented split unreliable.
_METHOD_RE = re.compile(r'"method":\s*"(\w+)"')
_URL_RE = re.compile(r'"url":\s*"([^"]+)"')


def _generated_operations() -> list[tuple[str, str, str, set[int]]]:
    operations = []
    for module in sorted(_API_DIR.rglob("*.py")):
        if module.name == "__init__.py":
            continue
        source = module.read_text()
        parse_response = next(
            (n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_parse_response"),
            None,
        )
        if parse_response is None:
            continue
        method = _METHOD_RE.search(source)
        url = _URL_RE.search(source)
        assert method and url, f"cannot read method/url out of {module.name} — has the generator's layout changed?"
        operations.append(
            (
                str(module.relative_to(_API_DIR)),
                method.group(1),
                url.group(1),
                _success_branches(parse_response),
            )
        )
    return operations


def test_every_operation_parses_its_success_response() -> None:
    """No operation may lose its success branch while the spec still declares one.

    The generator warns and continues when it cannot emit a model, so a dropped
    schema shows up here as a missing 2xx branch rather than as a failed build.
    That is what happened to ``GET /services/{service_id}``, and it went
    unnoticed across three releases — this asserts it for all of them at once.
    """
    operations = _generated_operations()
    assert operations, "no generated operations found — has the layout moved?"

    missing = [
        f"{method.upper()} {path} ({module}): spec declares a 2xx body, generated code handles none"
        for module, method, path, handled in operations
        if not handled and _spec_success_body(method, path) is not None
    ]

    assert not missing, "generated client dropped a success response:\n" + "\n".join(f"- {row}" for row in missing)
