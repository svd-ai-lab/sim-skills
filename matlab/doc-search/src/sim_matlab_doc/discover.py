"""Locate a MATLAB documentation root on the current host.

Priority:
  1. --matlab-root flag (caller's responsibility to pass)
  2. MATLAB_DOC_ROOT env var (points directly at the `help/` dir)
  3. MATLAB_ROOT / MATLABROOT env vars (point at the matlabroot install dir,
     e.g. /Applications/MATLAB_R2024b.app or C:\\Program Files\\MATLAB\\R2024b)
  4. `sim check matlab --json` (reuses sim-cli's install discovery; falls
     back to the legacy `ion` binary)
  5. Typical per-OS install paths

When multiple releases are present the newest is preferred. "Newest" is
determined by lexical comparison of the `Rxxxxy` folder name
(`R2024b > R2024a > R2023b`) — this matches MathWorks' release naming
convention, where a year's "b" release is always newer than its "a"
release and years sort numerically.

The returned path is always the `help/` dir itself, which contains one
subfolder per toolbox (`matlab/`, `simulink/`, `optim/`, …).
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path


DOC_SUBPATH = Path("help")


def _has_html_deep(d: Path) -> bool:
    """True if *any* .html file exists anywhere beneath `d`."""
    try:
        next(d.rglob("*.html"))
        return True
    except StopIteration:
        return False


def _looks_like_help_dir(candidate: Path) -> bool:
    """Validate that `candidate` is a MATLAB help/ tree.

    Core MATLAB help always ships at `help/matlab/` with HTML under it.
    Fall back to accepting any direct-child dir that contains HTML, so
    trimmed-down installs still work.
    """
    if not candidate.is_dir():
        return False
    core = candidate / "matlab"
    if core.is_dir() and _has_html_deep(core):
        return True
    for child in candidate.iterdir():
        if child.is_dir() and _has_html_deep(child):
            return True
    return False


def _as_doc_root(install_root: Path) -> Path | None:
    """Given a matlabroot (or help/ dir, or .app bundle), return the help/ tree if valid.

    Accepts:
      - A matlabroot like `/Applications/MATLAB_R2024b.app`,
        `C:\\Program Files\\MATLAB\\R2024b`, `/usr/local/MATLAB/R2024b`
        — appends `help/`.
      - A macOS `.app` bundle (which is itself a directory; `<bundle>/help/`
        exists inside it — same logic as the generic matlabroot case).
      - The `help/` dir itself (already contains toolbox folders).
    """
    if not install_root.is_dir():
        return None

    # Already the help/ dir?
    if _looks_like_help_dir(install_root):
        return install_root

    # Treat as a matlabroot — the .app bundle and Linux/Windows installs all
    # expose `help/` at the same relative position.
    candidate = install_root / DOC_SUBPATH
    if _looks_like_help_dir(candidate):
        return candidate

    return None


def _from_env() -> Path | None:
    doc = os.environ.get("MATLAB_DOC_ROOT")
    if doc:
        p = Path(doc)
        if _looks_like_help_dir(p):
            return p

    for var in ("MATLAB_ROOT", "MATLABROOT"):
        root = os.environ.get(var)
        if root:
            hit = _as_doc_root(Path(root))
            if hit:
                return hit
    return None


def _from_sim_check() -> Path | None:
    """Shell out to `sim check matlab --json` and take the first install."""
    for binary in ("sim", "ion"):
        try:
            proc = subprocess.run(
                [binary, "--json", "check", "matlab"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if proc.returncode != 0:
            continue
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue
        installs = payload.get("data", {}).get("installs") or []
        for entry in installs:
            p = entry.get("path")
            if not p:
                continue
            hit = _as_doc_root(Path(p))
            if hit:
                return hit
    return None


def _sorted_releases(paths: list[Path]) -> list[Path]:
    """Sort candidate install dirs newest-first by folder name (Rxxxxy)."""
    return sorted(paths, key=lambda p: p.name, reverse=True)


def _typical_macos_candidates() -> list[Path]:
    apps = Path("/Applications")
    if not apps.is_dir():
        return []
    hits = [p for p in apps.glob("MATLAB_R*.app") if p.is_dir()]
    return _sorted_releases(hits)


def _typical_windows_candidates() -> list[Path]:
    out: list[Path] = []
    for base in (
        Path(r"C:\Program Files\MATLAB"),
        Path(r"C:\Program Files (x86)\MATLAB"),
        Path(r"D:\Program Files\MATLAB"),
    ):
        if not base.is_dir():
            continue
        out.extend(p for p in base.glob("R*") if p.is_dir())
    return _sorted_releases(out)


def _typical_linux_candidates() -> list[Path]:
    out: list[Path] = []
    for base in (Path("/usr/local/MATLAB"), Path("/opt/MATLAB")):
        if not base.is_dir():
            continue
        out.extend(p for p in base.glob("R*") if p.is_dir())
    return _sorted_releases(out)


def _from_typical_paths() -> Path | None:
    system = platform.system()
    if system == "Darwin":
        candidates = _typical_macos_candidates()
    elif system == "Windows":
        candidates = _typical_windows_candidates()
    elif system == "Linux":
        candidates = _typical_linux_candidates()
    else:
        candidates = []

    for root in candidates:
        hit = _as_doc_root(root)
        if hit:
            return hit
    return None


def locate_doc_root(explicit: Path | None = None) -> Path:
    """Return the help/ tree root or raise FileNotFoundError."""
    if explicit is not None:
        hit = _as_doc_root(explicit)
        if hit:
            return hit
        raise FileNotFoundError(f"No MATLAB help tree under {explicit}")

    for finder in (_from_env, _from_sim_check, _from_typical_paths):
        hit = finder()
        if hit:
            return hit

    raise FileNotFoundError(
        "Could not locate MATLAB documentation. Set MATLAB_DOC_ROOT or MATLAB_ROOT, "
        "install sim-cli so `sim check matlab` can find the install, or pass --matlab-root."
    )
