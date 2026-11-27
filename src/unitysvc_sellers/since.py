"""``specs upload --since REF``: send only the services that changed since the branch left ``REF``.

A pull request's check has to test what the pull request changed and nothing else. The upload state
(``--state``) cannot say that: it records what was last sent to a target, so on a branch that is behind
its base every service changed on the base since then looks changed too, and would be sent in its older
form. Git can say it. The catalog as of the **merge base** of ``REF`` and ``HEAD`` is extracted, rendered
the same way as the working tree, and fingerprinted (:func:`unitysvc_sellers.upload.catalog_fingerprints`);
the upload then skips every service whose fingerprint is the same there.

The comparison is of expanded content, not of file paths, so a changed template, preset reference or
shared file counts for exactly the services it changes.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


class SinceError(ValueError):
    """``--since`` cannot be answered (no repository, an unknown ref, no common history)."""


def _git(cwd: Path, *args: str) -> bytes:
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)
    except OSError as exc:
        raise SinceError(f"git could not be run: {exc}") from exc
    if done.returncode != 0:
        raise SinceError(done.stderr.decode("utf-8", "replace").strip() or f"git {args[0]} failed")
    return done.stdout


def merge_base(ref: str, directory: Path) -> tuple[Path, str]:
    """The repository root and the commit where ``HEAD`` left ``ref``."""
    try:
        root = Path(_git(directory, "rev-parse", "--show-toplevel").decode().strip())
    except SinceError as exc:
        raise SinceError(f"--since needs a git repository: {exc}") from exc
    try:
        _git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except SinceError as exc:
        raise SinceError(f"--since: {ref!r} is not a commit of this repository (fetch it first).") from exc
    try:
        commit = _git(root, "merge-base", ref, "HEAD").decode().strip()
    except SinceError as exc:
        raise SinceError(
            f"--since: HEAD and {ref!r} have no common commit here. A shallow clone lacks it: fetch the "
            "full history (actions/checkout: fetch-depth: 0)."
        ) from exc
    return root, commit


def fingerprints_since(ref: str, directory: Path) -> tuple[dict[str, tuple[str, str]], str]:
    """Fingerprints of the catalog under ``directory`` as it was where ``HEAD`` left ``ref``, and that commit.

    ``directory`` is the folder the command was started in (the catalog root, inside a git repository).
    A catalog folder that did not exist at that commit has no fingerprints, so everything in it is sent.
    """
    from . import params_render
    from .upload import catalog_fingerprints

    directory = directory.resolve()
    root, commit = merge_base(ref, directory)
    relative = directory.relative_to(root.resolve())

    tmp = Path(tempfile.mkdtemp(prefix="usvc-since-"))
    cwd = Path.cwd()
    # The render changes the directory and records where the command was started; this one is nested in
    # the command's own render, so both are put back.
    invocation = params_render._invocation_cwd
    try:
        with tarfile.open(fileobj=io.BytesIO(_git(root, "archive", "--format=tar", commit))) as archive:
            archive.extractall(tmp, filter="data")
        base_dir = tmp / relative
        if not base_dir.is_dir():
            return {}, commit
        os.chdir(base_dir)
        try:
            with params_render.materialized_param_specs(Path.cwd()):
                fingerprints = catalog_fingerprints(Path.cwd())
        except params_render.ParamRenderError as exc:
            raise SinceError(f"--since: the catalog at {commit[:9]} cannot be rendered: {exc}") from exc
        return fingerprints, commit
    finally:
        os.chdir(cwd)
        params_render._invocation_cwd = invocation
        shutil.rmtree(tmp, ignore_errors=True)
