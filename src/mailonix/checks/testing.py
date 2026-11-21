"""Sirf tests ke liye: jaan boojh kar kharab checks. Registry mein KABHI nahi.

G1.3 ka orchestrator test inhein chala kar dekhega ke ek check toote ya der kare to bhi
poora scan chale, aur `ScanResult.unavailable` mein us ka naam aaye (Gate 1 shart #4).
"""

import asyncio

from mailonix.contracts import ParsedEmail, Signal

from .base import Check


class BrokenCheck(Check):
    name = "broken_check"
    group = "A"

    async def run(self, email: ParsedEmail) -> Signal:
        raise RuntimeError("jaan boojh kar toota hua check (test)")


class SlowCheck(Check):
    name = "slow_check"
    group = "A"
    default_params = {"sleep_seconds": 30.0}

    async def run(self, email: ParsedEmail) -> Signal:
        await asyncio.sleep(self.params["sleep_seconds"])
        return self.ok(0.0)
