"""Product-link reachability check (unitysvc/unitysvc#2873).

An offering's ``details.links`` maps display labels to the product's public
``https://`` pages (``homepage`` first among them). ``specs run-tests`` checks
that every one of them answers, as its last step and for every service, with or
without channels. Results are reported, never saved: a page that is down today
must be seen as down the next time the check runs.

The fetch follows the platform's rules for probing a public URL: ``https``
only, every hop's host must resolve to public addresses only (redirects are
followed by hand so each one is re-checked), a bounded number of redirects and
a short timeout. A final status below 400 is reachable, and so are 401, 403 and
429, which mean the site answered but refuses an anonymous client.
"""

from __future__ import annotations

import ipaddress
import socket
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from .utils import load_data_file

LINK_TIMEOUT_SECONDS = 15.0
MAX_REDIRECTS = 5
# Statuses at or above 400 that still prove the site answered: a login wall, a
# bot wall or a rate limit. The platform's check counts them the same way
# (unitysvc ``service_health_tasks.probe``), so both runs agree.
LINK_UP_STATUSES = frozenset({401, 403, 429})
_USER_AGENT = "unitysvc-link-check/1.0"


def offering_links(listing_file: Path) -> dict[str, str]:
    """Return the ``details.links`` of the offering next to ``listing_file``."""
    for offering_file in sorted(listing_file.parent.glob("offering.*")):
        if offering_file.suffix not in (".json", ".toml"):
            continue
        data, _ = load_data_file(offering_file)
        links = ((data or {}).get("details") or {}).get("links")
        if isinstance(links, dict):
            return {str(k): str(v) for k, v in links.items()}
        return {}
    return {}


def _public_host_error(host: str) -> str | None:
    """Why ``host`` may not be fetched, or ``None`` when every address is public."""
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        return f"cannot resolve {host}: {exc}"
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            return f"{host} resolves to a non-public address ({address})"
    return None


def check_link(url: str, *, client: httpx.Client) -> str | None:
    """Fetch ``url``; return why it is unreachable, or ``None`` when it answers."""
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        parts = urlsplit(current)
        if parts.scheme != "https" or not parts.hostname:
            return f"not an https:// URL: {current}"
        if error := _public_host_error(parts.hostname):
            return error
        try:
            with client.stream("GET", current) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        return f"HTTP {response.status_code} redirect without a Location"
                    current = urljoin(current, location)
                    continue
                if response.status_code >= 400 and response.status_code not in LINK_UP_STATUSES:
                    return f"HTTP {response.status_code}"
                return None
        except httpx.TimeoutException:
            return f"no answer within {LINK_TIMEOUT_SECONDS:g}s"
        except httpx.HTTPError as exc:
            return f"{type(exc).__name__}: {exc}"
    return f"more than {MAX_REDIRECTS} redirects"


def check_links(links: dict[str, str]) -> list[dict[str, Any]]:
    """Check each link; return one ``{name, url, ok, error}`` row per link."""
    rows: list[dict[str, Any]] = []
    with httpx.Client(
        follow_redirects=False,
        timeout=LINK_TIMEOUT_SECONDS,
        headers={"User-Agent": _USER_AGENT},
    ) as client:
        for name, url in links.items():
            error = check_link(url, client=client)
            rows.append({"name": name, "url": url, "ok": error is None, "error": error})
    return rows
