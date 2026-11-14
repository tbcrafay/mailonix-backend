"""Contract tests: shakal aur qaide. Logic ka koi test yahan nahi."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from mailonix.contracts import (
    Attachment, AttachmentDisposition, Disposition, HeaderField, Link, LinkSource,
    ParsedEmail, Reason, Remediation, ScanReason, ScanResult, Signal, SignalStatus, Verdict,
)

NOW = datetime(2026, 11, 7, 10, 15, tzinfo=timezone.utc)


def make_email(**kw) -> ParsedEmail:
    base = dict(
        email_id=uuid4(),
        received_at=NOW,
        envelope_from="ceo@ssuet-lab.test",
        envelope_to=("finance@ssuet-lab.test",),
        from_addr="ceo@ssuet-lab.test",
        from_name="CEO",
        reply_to="ceo.private@freemail.test",
        subject="Urgent payment",
        headers=(HeaderField(name="Received", value="a"), HeaderField(name="Received", value="b")),
        body_text="Please process this today.",
        links=(Link(url="http://pay-now.test/x", anchor_text="Click here", source=LinkSource.HTML_HREF),),
        attachments=(Attachment(content_type="application/pdf", size=10, sha256="a" * 64,
                                disposition=AttachmentDisposition.ATTACHMENT, stored_path="att/1.bin"),),
        raw_path="raw/1.eml",
    )
    base.update(kw)
    return ParsedEmail(**base)


def ok_signal(**kw) -> Signal:
    base = dict(module="header_auth", status=SignalStatus.OK, value=0.8,
                reasons=(Reason(code="reply_to_mismatch", text="Reply-To From se alag hai"),))
    base.update(kw)
    return Signal(**base)


def make_result(**kw) -> ScanResult:
    base = dict(
        email_id=uuid4(), score=81.0, verdict=Verdict.HIGH, action=Disposition.DELIVER,
        remediations=(Remediation.BANNER, Remediation.STRIP_LINKS),
        reasons=(ScanReason(signal="header_auth", code="reply_to_mismatch", contribution=20.0, text="x"),),
        signals=(ok_signal(),), config_version="default", scanned_at=NOW, latency_ms=120.0,
    )
    base.update(kw)
    return ScanResult(**base)


# ---- ParsedEmail ----

def test_parsed_email_roundtrip_json():
    e = make_email()
    assert ParsedEmail.model_validate_json(e.model_dump_json()) == e


def test_duplicate_headers_keep_order():
    e = make_email()
    assert [h.value for h in e.headers if h.name == "Received"] == ["a", "b"]


def test_parsed_email_is_immutable():
    e = make_email()
    with pytest.raises(ValidationError):
        e.subject = "changed"


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        make_email(subjekt="typo")


def test_naive_datetime_rejected():
    with pytest.raises(ValidationError):
        make_email(received_at=datetime(2026, 11, 7, 10, 15))


def test_bad_sha256_rejected():
    with pytest.raises(ValidationError):
        Attachment(content_type="x", size=1, sha256="XYZ",
                   disposition=AttachmentDisposition.ATTACHMENT, stored_path="p")


# ---- Signal ----

def test_ok_needs_value():
    with pytest.raises(ValidationError):
        Signal(module="x", status=SignalStatus.OK)


@pytest.mark.parametrize("status", [SignalStatus.UNAVAILABLE, SignalStatus.ABSTAINED])
def test_non_ok_must_not_have_value(status):
    with pytest.raises(ValidationError):
        Signal(module="x", status=status, value=0.0)
    assert Signal(module="x", status=status).value is None


@pytest.mark.parametrize("v", [-0.01, 1.01])
def test_value_range(v):
    with pytest.raises(ValidationError):
        ok_signal(value=v)


def test_module_name_format():
    with pytest.raises(ValidationError):
        ok_signal(module="Header Auth")


def test_latency_filled_by_copy():
    s = ok_signal()
    s2 = s.model_copy(update={"latency_ms": 41.0})
    assert s.latency_ms == 0.0 and s2.latency_ms == 41.0


# ---- ScanResult ----

def test_scan_result_roundtrip_json():
    r = make_result()
    assert ScanResult.model_validate_json(r.model_dump_json()) == r


def test_unscanned_has_no_score():
    r = make_result(score=None, verdict=Verdict.UNSCANNED,
                    remediations=(Remediation.UNSCANNED_BANNER,), signals=())
    assert r.score is None


def test_score_none_only_when_unscanned():
    with pytest.raises(ValidationError):
        make_result(score=None, verdict=Verdict.LOW)
    with pytest.raises(ValidationError):
        make_result(score=10.0, verdict=Verdict.UNSCANNED)


def test_score_range():
    with pytest.raises(ValidationError):
        make_result(score=100.5)


# ---- Enums frozen ----

def test_enum_values_frozen():
    assert [s.value for s in SignalStatus] == ["ok", "unavailable", "abstained"]
    assert [v.value for v in Verdict] == ["low", "medium", "high", "critical", "unscanned"]
    assert [d.value for d in Disposition] == ["deliver", "quarantine", "block"]
    assert [r.value for r in Remediation] == ["banner", "strip_links", "isolate_attachment", "unscanned_banner"]
