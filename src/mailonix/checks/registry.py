"""Kaun se checks chalenge.

Naya check jorna:
  1. checks/ mein nayi file, class `Check` se (base.py dekho)
  2. neeche ALL_CHECKS mein ek line
  3. us ki badalne wali values config/checks.toml mein [naam] ke neeche

Band karna (bina code chhede): .env mein  DISABLED_CHECKS=intent,links
Values badalna: config/checks.toml (file ka path .env ke CHECKS_CONFIG se)
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mailonix.config import Settings, get_settings

from .attachments import AttachmentsCheck
from .base import Check, CheckConfigError
from .behaviour import BehaviourCheck
from .header_auth import HeaderAuthCheck
from .intent import IntentCheck
from .links import LinksCheck
from .threat_intel import ThreatIntelCheck

# Tarteeb = SRS ke groups A se F. Checks ek saath chalte hain, tarteeb sirf parhne ke liye.
ALL_CHECKS: tuple[type[Check], ...] = (
    HeaderAuthCheck,    # A
    ThreatIntelCheck,   # B (placeholder)
    LinksCheck,         # C (placeholder)
    AttachmentsCheck,   # D (placeholder)
    BehaviourCheck,     # E (placeholder)
    IntentCheck,        # F (placeholder)
)


@dataclass(frozen=True)
class LoadedChecks:
    checks: tuple[Check, ...]
    disabled: tuple[str, ...]
    fingerprint: str  # ScanResult.config_version ka hissa: kaun se checks, kin values par

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.checks)


def _validate_classes(classes: Sequence[type[Check]]) -> None:
    seen: set[str] = set()
    for cls in classes:
        cls.validate_class()
        if cls.name in seen:
            raise TypeError(f"Do checks ka ek hi naam: {cls.name}")
        seen.add(cls.name)


def read_checks_config(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        raise CheckConfigError(f"Checks ki config file nahi mili: {path} (CHECKS_CONFIG dekho)")
    with path.open("rb") as f:
        data = tomllib.load(f)
    for key, value in data.items():
        if not isinstance(value, dict):
            raise CheckConfigError(f"{path}: '{key}' ek [section] hona chahiye")
    return data


def load_checks(
    settings: Settings | None = None,
    classes: Sequence[type[Check]] = ALL_CHECKS,
) -> LoadedChecks:
    settings = settings or get_settings()
    _validate_classes(classes)
    known = {cls.name for cls in classes}

    config = read_checks_config(settings.checks_config)
    unknown_sections = set(config) - known
    if unknown_sections:
        raise CheckConfigError(f"checks.toml mein anjaan checks: {sorted(unknown_sections)}. Jaiz: {sorted(known)}")

    disabled = settings.disabled_check_names
    unknown_disabled = set(disabled) - known
    if unknown_disabled:
        raise CheckConfigError(f"DISABLED_CHECKS mein anjaan naam: {sorted(unknown_disabled)}. Jaiz: {sorted(known)}")

    checks = tuple(cls(config.get(cls.name)) for cls in classes if cls.name not in disabled)

    snapshot = {
        "checks": {c.name: c.params for c in checks},
        "disabled": sorted(disabled),
    }
    fingerprint = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()[:12]
    return LoadedChecks(checks=checks, disabled=tuple(sorted(disabled)), fingerprint=fingerprint)
