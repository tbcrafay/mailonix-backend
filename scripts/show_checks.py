"""Saare chalne wale checks ek namoona email par chala kar un ka jawab dikhata hai.

    python scripts/show_checks.py              # saaf email
    python scripts/show_checks.py --mismatch   # Reply-To ka domain alag

Sirf dekhne ke liye: parser aur orchestrator abhi nahi bane, is liye email haath se banti hai.
"""

import argparse
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from mailonix.checks import load_checks
from mailonix.contracts import ParsedEmail


def sample_email(mismatch: bool) -> ParsedEmail:
    return ParsedEmail(
        email_id=uuid4(),
        received_at=datetime.now(timezone.utc),
        envelope_from="ceo@ssuet-lab.test",
        envelope_to=("finance@ssuet-lab.test",),
        from_addr="ceo@ssuet-lab.test",
        from_name="CEO",
        reply_to="ceo.private@freemail.test" if mismatch else None,
        subject="Urgent payment",
        body_text="Please process this today.",
        raw_path="(namoona)",
    )


async def main(mismatch: bool) -> None:
    loaded = load_checks()
    email = sample_email(mismatch)
    print(f"Chalne wale checks: {len(loaded.checks)}   band: {list(loaded.disabled) or '-'}   fingerprint: {loaded.fingerprint}\n")
    print(f"{'check':<14}{'group':<7}{'status':<13}{'value':<7}wajah")
    print("-" * 78)
    for check in loaded.checks:
        sig = await check.run(email)
        value = "-" if sig.value is None else f"{sig.value:.2f}"
        why = "; ".join(r.text for r in sig.reasons) or "-"
        print(f"{check.name:<14}{check.group:<7}{sig.status.value:<13}{value:<7}{why}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mismatch", action="store_true", help="Reply-To ka domain From se alag rakho")
    asyncio.run(main(ap.parse_args().mismatch))
