"""Sab tests ke liye shared cheezein.

`make_email` fixture: bina parser ke test email (ParsedEmail) banata hai. Checks isi se test hote hain.
Sirf woh fields do jo tumhare check ko chahiyen, baqi defaults se bharenge:

    async def test_mera_check(make_email):
        email = make_email(reply_to="x@other.test", links=(...,))
        signal = await MeraCheck().run(email)

Defaults ek saaf, aam email jaise hain. Jab parser (G1.2) aayega to yeh defaults us ke asli output
jaise kiye jayenge (maslan address chhote huroof mein hon ya nahi), aur har check asli .eml par bhi chalega.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from mailonix.contracts import HeaderField, ParsedEmail

FIXED_TIME = datetime(2026, 11, 22, 10, 0, tzinfo=timezone.utc)


def _make_email(**overrides) -> ParsedEmail:
    base = dict(
        email_id=uuid4(),
        message_id="<test-1@ssuet-lab.test>",
        received_at=FIXED_TIME,
        connecting_ip="203.0.113.10",
        helo="mail.ssuet-lab.test",
        envelope_from="ali@ssuet-lab.test",
        envelope_to=("finance@ssuet-lab.test",),
        from_addr="ali@ssuet-lab.test",
        from_name="Ali",
        reply_to=None,
        to=("finance@ssuet-lab.test",),
        subject="Weekly report",
        headers=(HeaderField(name="From", value="Ali <ali@ssuet-lab.test>"),),
        body_text="Please find the weekly report attached.",
        raw_path="tests/samples/none.eml",
    )
    base.update(overrides)
    return ParsedEmail(**base)


@pytest.fixture
def make_email():
    return _make_email
