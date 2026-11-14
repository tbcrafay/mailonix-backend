"""ScanResult: fusion + policy ka nateeja. Orchestrator isi ek object se emails/scan_results/signals bharta hai. Contract v1.0."""

from uuid import UUID

from pydantic import AwareDatetime, Field, model_validator

from .base import Contract
from .enums import Disposition, Remediation, Verdict
from .signal import Signal


class ScanReason(Contract):
    signal: str          # module ka naam (override ho to bhi trigger karne wala module)
    code: str            # Signal.Reason ka code, ya "override.<naam>" (FR-8.2)
    contribution: float  # score mein kitne points (0-100 ke paimane par)
    text: str


class ScanResult(Contract):
    email_id: UUID
    score: float | None = Field(ge=0.0, le=100.0)  # sirf UNSCANNED par None
    verdict: Verdict
    action: Disposition
    remediations: tuple[Remediation, ...] = ()
    reasons: tuple[ScanReason, ...] = ()           # bara contribution pehle (FR-8.3)
    unavailable: tuple[str, ...] = ()              # module naam
    abstained: tuple[str, ...] = ()                # module naam
    signals: tuple[Signal, ...] = ()
    config_version: str                            # kaun se weights/thresholds/policy lage (admin badal sakta hai)
    scanned_at: AwareDatetime
    latency_ms: float = Field(ge=0.0)              # poora scan (S7: p95 naapne ke liye)

    @model_validator(mode="after")
    def _score_matches_verdict(self) -> "ScanResult":
        if (self.verdict is Verdict.UNSCANNED) != (self.score is None):
            raise ValueError("score None tab, aur sirf tab, jab verdict=unscanned")
        return self
