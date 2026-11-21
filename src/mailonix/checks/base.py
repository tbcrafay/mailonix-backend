"""Har check ka saancha.

Ek check = ek class jo `Check` se banti hai:
    name   : registry wala naam, snake_case (Signal.module isi se bharta hai)
    group  : SRS ka jaanch group, "A" se "F"
    default_params : check ki badalne wali values; config/checks.toml inhein badal sakti hai
    async run(email) -> Signal

Qaide (gate1-context section 8):
1. Check sirf Signal deta hai; email ko badalta ya rokta nahi (ParsedEmail frozen hai).
2. Check database mein kabhi nahi likhta.
3. Error ya timeout orchestrator pakarta hai aur `unavailable` banata hai; check khud bhi
   jaani pehchani nakami par `self.unavailable(...)` de sakta hai.
4. Data kam ho to `self.abstain(...)`: "meri raye nahi". Kabhi "0 = safe" mat do jab pata hi na ho.
5. Check ki `value` us ki apni raye hai (0 = koi shak nahi, 1 = pakka khatra). Weight fusion ka kaam hai.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any, ClassVar

from mailonix.contracts import ParsedEmail, Reason, Signal, SignalStatus

GROUPS = ("A", "B", "C", "D", "E", "F")
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class CheckConfigError(ValueError):
    """config/checks.toml ya DISABLED_CHECKS mein ghalti."""


def reason(code: str, text: str) -> Reason:
    return Reason(code=code, text=text)


class Check(ABC):
    name: ClassVar[str]
    group: ClassVar[str]
    default_params: ClassVar[Mapping[str, Any]] = {}

    def __init__(self, params: Mapping[str, Any] | None = None) -> None:
        params = dict(params or {})
        unknown = set(params) - set(self.default_params)
        if unknown:
            raise CheckConfigError(
                f"[{self.name}] ke liye anjaan setting(s): {sorted(unknown)}. "
                f"Jaiz: {sorted(self.default_params)}"
            )
        self.params: dict[str, Any] = {**self.default_params, **params}

    @classmethod
    def validate_class(cls) -> None:
        """Registry har check par yeh chalati hai: naam aur group sahi hon."""
        if not _NAME_RE.match(getattr(cls, "name", "") or ""):
            raise TypeError(f"{cls.__name__}.name snake_case hona chahiye")
        if getattr(cls, "group", None) not in GROUPS:
            raise TypeError(f"{cls.__name__}.group {GROUPS} mein se hona chahiye")

    @abstractmethod
    async def run(self, email: ParsedEmail) -> Signal: ...

    # --- Signal banane ke helpers: module ka naam khud bhar dete hain ---

    def ok(self, value: float, reasons: Iterable[Reason] = (), details: Mapping[str, Any] | None = None) -> Signal:
        return Signal(module=self.name, status=SignalStatus.OK, value=value,
                      reasons=tuple(reasons), details=dict(details or {}))

    def abstain(self, code: str, text: str, details: Mapping[str, Any] | None = None) -> Signal:
        return Signal(module=self.name, status=SignalStatus.ABSTAINED,
                      reasons=(reason(code, text),), details=dict(details or {}))

    def unavailable(self, code: str, text: str, details: Mapping[str, Any] | None = None) -> Signal:
        return Signal(module=self.name, status=SignalStatus.UNAVAILABLE,
                      reasons=(reason(code, text),), details=dict(details or {}))


class PlaceholderCheck(Check, ABC):
    """Jo check abhi bana nahi: hamesha `abstained` deta hai, taake fusion usay "safe" na samjhe.
    Asli version aane par class `Check` se banegi aur yeh base hat jayega."""

    async def run(self, email: ParsedEmail) -> Signal:
        return self.abstain("not_implemented", f"{self.name} abhi bana nahi (placeholder)")
