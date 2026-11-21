"""Command-scoped preset refresh without changing the installed CLI environment."""

from __future__ import annotations

import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterator, MutableMapping
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache, partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

import unitysvc_data
from filelock import FileLock, Timeout
from packaging.version import Version

logger = logging.getLogger(__name__)
_GENERATION_LOCK = threading.Lock()
_HELPER = Path(__file__).with_name("_preset_helper.py")
_INDEX = "https://pypi.org/simple"
_ENV_KEYS = ("PATH", "SYSTEMROOT", "WINDIR", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "TMP", "TEMP", "TMPDIR")


class MissingPreset(KeyError):
    """A named preset is unavailable, rather than an invalid parameter/recipe."""


class HelperFailure(ValueError):
    """Cached code could not be loaded/executed or returned an invalid response."""


@dataclass(frozen=True)
class CachedRelease:
    directory: Path
    version: str


def _environment() -> dict[str, str]:
    return {key: os.environ[key] for key in _ENV_KEYS if key in os.environ}


class PresetResolver:
    def __init__(
        self, cache_dir: Path, *, refresh_timeout: float = 60, replay_timeout: float = 15, cooldown: float = 60
    ) -> None:
        self.cache_dir = cache_dir
        self.refresh_timeout = refresh_timeout
        self.replay_timeout = replay_timeout
        self.cooldown = cooldown
        self.bundled = dict(unitysvc_data.PRESET_FNS)
        # Catalogs reuse the same recipes many times. Cache immutable results
        # within this command; callers receive copies they can safely modify.
        self._cached_expand = lru_cache(maxsize=256)(self._expand)

    def _active(self) -> CachedRelease | None:
        try:
            info = json.loads((self.cache_dir / "active.json").read_text())
            name, version = info["directory"], info["version"]
            if not isinstance(name, str) or re.fullmatch(r"release-[a-f0-9]{32}", name) is None:
                raise ValueError("Invalid cache directory")
            parsed = Version(version)
            if parsed.is_prerelease or parsed.is_devrelease:
                raise ValueError("Expected a stable release")
            if parsed < Version(unitysvc_data.__version__):
                return None
            directory = self.cache_dir / name
            if not directory.is_dir():
                raise ValueError("Cached release directory is missing")
            return CachedRelease(directory, version)
        except FileNotFoundError:
            return None
        except (OSError, ValueError, KeyError, TypeError):
            logger.warning("Ignoring unusable unitysvc-data cache; using the installed package")
            return None

    def _bundled(self, function: str, value: Any) -> Any:
        try:
            # The library's materialized-file cache uses non-atomic writes.
            with _GENERATION_LOCK:
                return self.bundled[function](value)
        except KeyError as exc:
            if exc.args and str(exc.args[0]).startswith("Unknown preset:"):
                raise MissingPreset(str(exc.args[0]).split(". Available ", 1)[0]) from exc
            raise

    def _helper(self, package: Path, request: dict[str, Any]) -> Any:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            with TemporaryDirectory(dir=self.cache_dir, prefix=".request-") as scratch:
                completed = subprocess.run(
                    [sys.executable, "-I", str(_HELPER), str(package), str(self.cache_dir / "assets"), scratch],
                    input=json.dumps(request),
                    env=_environment(),
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=self.replay_timeout,
                )
            response = json.loads(completed.stdout)
            if not isinstance(response, dict):
                raise HelperFailure("Malformed preset helper response")
            status = response.get("status")
            if status == "missing":
                raise MissingPreset(str(response.get("error")))
            if status == "invalid":
                raise ValueError(str(response.get("error")))
            if status != "ok" or "result" not in response:
                raise HelperFailure("Malformed preset helper response")
            return response["result"]
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            raise HelperFailure("Cached unitysvc-data could not expand the preset") from exc

    def _call(self, release: CachedRelease | None, function: str, value: Any) -> Any:
        if release is None:
            return self._bundled(function, value)
        return deepcopy(self._cached_expand(release.directory, function, json.dumps(value, sort_keys=True)))

    def _expand(self, directory: Path, function: str, serialized: str) -> Any:
        return self._helper(directory, {"operation": "expand", "function": function, "value": json.loads(serialized)})

    def call(self, function: str, value: Any) -> Any:
        release = self._active()
        repair = False
        try:
            return self._call(release, function, value)
        except HelperFailure:
            logger.warning("Cached unitysvc-data failed; trying the installed package")
            try:
                return self._bundled(function, value)
            except MissingPreset:
                repair = True
        except MissingPreset:
            pass
        attempted = False
        try:
            refreshed, attempted = self._refresh(release, repair=repair)
            try:
                return self._call(refreshed, function, value)
            except HelperFailure:
                return self._bundled(function, value)
        except MissingPreset as exc:
            state = "after refreshing unitysvc-data" if attempted else "during the preset refresh cooldown"
            raise ValueError(f"Preset is unavailable {state}; check its name or retry later. {exc}") from exc
        except (OSError, Timeout, subprocess.SubprocessError) as exc:
            raise ValueError("Could not refresh unitysvc-data; check network access and cache permissions.") from exc

    def _refresh(self, observed: CachedRelease | None, *, repair: bool = False) -> tuple[CachedRelease | None, bool]:
        self.cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        deadline = time.monotonic() + self.refresh_timeout
        with FileLock(str(self.cache_dir / ".refresh.lock"), timeout=self.refresh_timeout):
            current = self._active()
            if current != observed:
                return current, True
            stamp = self.cache_dir / ".last-refresh"
            if stamp.exists() and time.time() - stamp.stat().st_mtime < self.cooldown:
                return current, False
            logger.info("Refreshing unitysvc-data for an unavailable preset")
            try:
                return self._install(current, deadline=deadline, repair=repair), True
            finally:
                stamp.touch()

    def _install(self, current: CachedRelease | None, *, deadline: float, repair: bool) -> CachedRelease | None:
        # Drop local/dev suffixes so pip's default resolver never opts into prereleases.
        minimum = current.version if current else Version(unitysvc_data.__version__).base_version
        with TemporaryDirectory(dir=self.cache_dir, prefix=".install-") as temporary:
            target = Path(temporary) / "package"
            common = [
                "install",
                "--target",
                str(target),
                "--index-url",
                _INDEX,
                "--only-binary",
                ":all:",
                "--no-deps",
                f"unitysvc-data>={minimum}",
            ]
            uv = shutil.which("uv")
            command = (
                [
                    uv,
                    "--no-config",
                    "--no-cache",
                    "pip",
                    *common,
                    "--prerelease",
                    "disallow",
                    "--python",
                    sys.executable,
                ]
                if uv
                else [
                    sys.executable,
                    "-m",
                    "pip",
                    "--isolated",
                    "--disable-pip-version-check",
                    "--no-cache-dir",
                    "--no-input",
                    *common,
                ]
            )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Preset refresh deadline expired")
            subprocess.run(
                command,
                env=_environment(),
                cwd=temporary,
                capture_output=True,
                text=True,
                check=True,
                timeout=remaining,
            )
            info = self._helper(target, {"operation": "probe"})
            if not isinstance(info, dict) or not isinstance(info.get("version"), str):
                raise HelperFailure("Invalid unitysvc-data installation")
            version = Version(info["version"])
            if version.is_prerelease or version.is_devrelease or version < Version(minimum):
                raise HelperFailure("Expected a compatible stable unitysvc-data release")
            if not set(self.bundled).issubset(info.get("functions", [])):
                raise HelperFailure("The release removed a required preset function")
            if version == Version(minimum) and not repair:
                return current
            directory = self.cache_dir / f"release-{uuid4().hex}"
            target.rename(directory)
            pointer = Path(temporary) / "active.json"
            pointer.write_text(json.dumps({"directory": directory.name, "version": str(version)}))
            pointer.replace(self.cache_dir / "active.json")
            logger.info("Using unitysvc-data %s from the preset cache", version)
            return CachedRelease(directory, str(version))


def _setting(name: str, default: float, *, allow_zero: bool = False) -> float:
    value = float(os.environ.get(f"UNITYSVC_SELLER_PRESET_{name}", default))
    if not math.isfinite(value) or value < 0 or (not allow_zero and value == 0):
        raise ValueError(f"Invalid UNITYSVC_SELLER_PRESET_{name}")
    return value


def resolver_from_environment() -> PresetResolver:
    base = os.environ.get("LOCALAPPDATA" if os.name == "nt" else "XDG_CACHE_HOME")
    default = (Path(base) if base else Path.home() / ".cache") / "unitysvc-sellers" / "presets"
    return PresetResolver(
        Path(os.environ.get("UNITYSVC_SELLER_PRESET_CACHE_DIR", str(default))).expanduser().resolve(),
        refresh_timeout=_setting("REFRESH_TIMEOUT_SECONDS", 60),
        replay_timeout=_setting("REPLAY_TIMEOUT_SECONDS", 15),
        cooldown=_setting("REFRESH_COOLDOWN_SECONDS", 60, allow_zero=True),
    )


@contextmanager
def refreshing_presets(resolver: PresetResolver | None = None) -> Iterator[None]:
    """Use core's existing walker and validator with command-scoped factory wrappers.

    Core's default registry is shared by its loader, discovery and validator.
    Restore it on command exit; importing the SDK does not change core behavior.
    """
    from unitysvc_core.utils import DEFAULT_PRESET_FNS

    if not isinstance(DEFAULT_PRESET_FNS, MutableMapping):
        raise TypeError("unitysvc-core does not expose a mutable default preset registry")
    registry: MutableMapping[str, Callable[[Any], Any]] = DEFAULT_PRESET_FNS
    original = dict(registry)
    resolver = resolver or resolver_from_environment()
    try:
        registry.update(
            {
                name: partial(resolver.call, name)
                for name, function in original.items()
                if function is unitysvc_data.PRESET_FNS.get(name)
            }
        )
        yield
    finally:
        registry.clear()
        registry.update(original)
