"""Execute one cached unitysvc-data operation in a fresh, isolated interpreter.

This file is run directly with ``python -I``; do not import the seller SDK here.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def persist_files(value: Any, roots: tuple[Path, ...], assets: Path) -> Any:
    """Keep generated/bundled files alive after this helper's scratch dir exits."""
    if isinstance(value, list):
        return [persist_files(item, roots, assets) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: persist_files(item, roots, assets) for key, item in value.items()}
    source = result.get("file_path")
    if isinstance(source, str):
        path = Path(source).resolve()
        # Opaque seller metadata is not an instruction to copy arbitrary files.
        if path.is_file() and any(path.is_relative_to(root) for root in roots):
            content = path.read_bytes()
            directory = assets / hashlib.sha256(content).hexdigest()
            directory.mkdir(parents=True, exist_ok=True)
            destination = directory / path.name
            if not destination.exists():
                descriptor, temporary = tempfile.mkstemp(dir=directory)
                try:
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(content)
                    os.replace(temporary, destination)
                finally:
                    Path(temporary).unlink(missing_ok=True)
            result["file_path"] = str(destination)
    return result


def main() -> None:
    package, assets, scratch = (Path(arg).resolve() for arg in sys.argv[1:])
    sys.path.insert(0, str(package))
    tempfile.tempdir = str(scratch)
    import unitysvc_data

    root = Path(unitysvc_data.__file__).resolve().parent
    if not root.is_relative_to(package):
        raise ValueError("unitysvc-data was not loaded from the requested installation.")
    request = json.load(sys.stdin)
    try:
        if request["operation"] == "probe":
            if not unitysvc_data.MANIFEST["presets"]:
                raise ValueError("The release contains no document presets.")
            for name in unitysvc_data.MANIFEST["presets"]:
                Path(unitysvc_data.doc_preset(name)["file_path"]).read_bytes()
            result: Any = {"version": unitysvc_data.__version__, "functions": sorted(unitysvc_data.PRESET_FNS)}
        else:
            result = unitysvc_data.PRESET_FNS[request["function"]](request["value"])
            result = persist_files(result, (root, scratch), assets)
        response = {"status": "ok", "result": result}
    except KeyError as exc:
        missing = bool(exc.args and str(exc.args[0]).startswith("Unknown preset:"))
        error = str(exc.args[0]).split(". Available ", 1)[0] if missing else str(exc)
        response = {"status": "missing" if missing else "invalid", "error": error}
    except (ValueError, TypeError) as exc:
        response = {"status": "invalid", "error": str(exc)}
    json.dump(response, sys.stdout)


if __name__ == "__main__":
    main()
