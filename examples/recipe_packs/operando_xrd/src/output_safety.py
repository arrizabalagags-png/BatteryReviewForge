"""Reserve a fresh output name without replacing a previous scientific result."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path


@contextmanager
def reserve_stem(stem: str | Path, suffixes: tuple[str, ...]):
    """An exclusive sibling lock protects concurrent runs; existing files version.

    The first run keeps the requested basename. Further runs use _v002, _v003.
    A failed run keeps its partial files for inspection, but releases its lock.
    """
    requested = Path(stem)
    requested.parent.mkdir(parents=True, exist_ok=True)
    version = 1
    while True:
        candidate = requested if version == 1 else requested.with_name(f"{requested.name}_v{version:03d}")
        lock = candidate.parent / f".{candidate.name}.export.lock"
        if any(Path(str(candidate) + suffix).exists() for suffix in suffixes):
            version += 1
            continue
        try:
            handle = lock.open("x", encoding="utf-8")
        except FileExistsError:
            version += 1
            continue
        if any(Path(str(candidate) + suffix).exists() for suffix in suffixes):
            handle.close()
            lock.unlink()
            version += 1
            continue
        break
    try:
        yield candidate, version
    finally:
        handle.close()
        lock.unlink(missing_ok=True)


def new_directory(requested: str | Path) -> tuple[Path, int]:
    """Atomically create a new directory, adding a version when necessary."""
    requested = Path(requested)
    requested.parent.mkdir(parents=True, exist_ok=True)
    version = 1
    while True:
        path = requested if version == 1 else requested.with_name(f"{requested.name}_v{version:03d}")
        try:
            path.mkdir()
            return path, version
        except FileExistsError:
            version += 1
