"""Hermes plugin for the file-backed passport lookup adapter.

Copy this whole directory to the Daniyar profile's plugins/passport-lookup/
directory. It has no business data and no dependency on the sales skills.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "daniyar_passport_lookup_adapter",
    Path(__file__).with_name("passport_lookup.py"),
)
if _spec is None or _spec.loader is None:  # pragma: no cover - import guard
    raise ImportError("Cannot load passport_lookup.py beside the plugin")
_adapter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_adapter)


def register(ctx) -> None:
    """Register one read-only tool; Hermes enables it only for this profile."""
    ctx.register_tool(
        name="passport_lookup",
        toolset="passport",
        schema=_adapter.HERMES_TOOL_SCHEMA,
        handler=_adapter.hermes_handler,
        check_fn=_adapter.hermes_check,
        emoji="📇",
    )
