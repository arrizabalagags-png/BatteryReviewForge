"""Deterministic, source-aware assembly of manuscript figure panels."""

from .layout import ComposeError, load_manifest, resolve_layout
from .render import compose

__all__ = ["ComposeError", "load_manifest", "resolve_layout", "compose"]
