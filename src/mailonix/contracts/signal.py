"""Signal: har check ka output. Contract v1.0.

Interface: async def run(email: ParsedEmail) -> Signal
"""

from typing import Any

from pydantic import Field, model_validator

from .base import Contract
from .enums import SignalStatus


class Reason(Contract):
    code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")  # mashine ke liye, maslan "reply_to_mismatch"
    text: str                                          # analyst/banner ke liye chhota jumla


class Signal(Contract):
    module: str = Field(pattern=r"^[a-z][a-z0-9_]*$")  # registry wala naam, maslan "header_auth"
    status: SignalStatus
    value: float | None = Field(default=None, ge=0.0, le=1.0)  # sirf OK par; check ki apni raye, weight nahi
    reasons: tuple[Reason, ...] = ()
    details: dict[str, Any] = Field(default_factory=dict)      # JSON-serializable hona chahiye
    latency_ms: float = Field(default=0.0, ge=0.0)             # orchestrator naap kar bharta hai

    @model_validator(mode="after")
    def _value_matches_status(self) -> "Signal":
        if self.status is SignalStatus.OK and self.value is None:
            raise ValueError("status=ok par value zaroori hai")
        if self.status is not SignalStatus.OK and self.value is not None:
            raise ValueError("value sirf status=ok par ho sakti hai")
        return self
