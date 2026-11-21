"""Database tests. PostgreSQL chalna chahiye (docker compose up -d) aur `alembic upgrade head` ho chuka ho.

Database na mile to yeh tests skip hote hain, fail nahi; contract tests phir bhi chalte hain.
Har test apni transaction mein chalta hai aur aakhir mein rollback, to DB mein kuch nahi bachta.
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from mailonix.contracts import Disposition, ParseStatus, SignalStatus, Verdict
from mailonix.db import Email, ScanResultRow, SignalRow, make_engine

NOW = datetime(2026, 11, 14, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def engine():
    eng = make_engine()
    try:
        with eng.connect() as c:
            c.execute(text("select 1"))
    except OperationalError:
        pytest.skip("PostgreSQL nahi mila: `docker compose up -d` chalao aur .env mein DATABASE_URL dekho")
    if not {"emails", "scan_results", "signals", "users"} <= set(inspect(eng).get_table_names()):
        pytest.fail("Database mil gaya lekin tables nahi: pehle `alembic upgrade head` chalao", pytrace=False)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine):
    conn = engine.connect()
    trans = conn.begin()
    s = Session(bind=conn, join_transaction_mode="create_savepoint")
    yield s
    s.close()
    trans.rollback()
    conn.close()


def make_email() -> Email:
    return Email(
        id=uuid.uuid4(), message_id="<a@ssuet-lab.test>", envelope_from="ceo@ssuet-lab.test",
        from_addr="ceo@ssuet-lab.test", recipients=["finance@ssuet-lab.test"], subject="Urgent",
        received_at=NOW, parse_status=ParseStatus.OK, raw_path="raw/1.eml",
    )


def make_scan(email_id, **kw) -> ScanResultRow:
    base = dict(
        email_id=email_id, score=81.0, verdict=Verdict.HIGH, action=Disposition.DELIVER,
        remediations=["banner"], reasons=[{"signal": "header_auth", "code": "x", "contribution": 20.0, "text": "t"}],
        unavailable=[], abstained=[], config_version="default", scanned_at=NOW, latency_ms=120.0,
    )
    base.update(kw)
    return ScanResultRow(**base)


def test_migration_applied(engine):
    tables = set(inspect(engine).get_table_names())
    missing = {"users", "emails", "scan_results", "signals", "alembic_version"} - tables
    assert not missing, f"tables nahi mile: {missing}. `alembic upgrade head` chalao"


def test_insert_email_scan_signals(session):
    e = make_email()
    scan = make_scan(e.id)
    scan.signals = [
        SignalRow(module="header_auth", status=SignalStatus.OK, value=0.8,
                  reasons=[{"code": "reply_to_mismatch", "text": "t"}], details={}, latency_ms=4.0),
        SignalRow(module="broken_check", status=SignalStatus.UNAVAILABLE, value=None,
                  reasons=[], details={"error": "timeout"}, latency_ms=10000.0),
    ]
    session.add_all([e, scan])
    session.flush()

    got = session.scalars(select(ScanResultRow).where(ScanResultRow.email_id == e.id)).one()
    assert got.verdict is Verdict.HIGH
    assert {s.module for s in got.signals} == {"header_auth", "broken_check"}
    # DB mein enum lowercase string ki tarah save hota hai
    raw = session.execute(text("select verdict from scan_results where id = :i"), {"i": got.id}).scalar()
    assert raw == "high"


def test_unscanned_needs_null_score(session):
    e = make_email()
    session.add(e)
    session.flush()
    session.add(make_scan(e.id, score=50.0, verdict=Verdict.UNSCANNED))
    with pytest.raises(IntegrityError):
        session.flush()


def test_signal_value_range_enforced(session):
    e = make_email()
    scan = make_scan(e.id)
    scan.signals = [SignalRow(module="x", status=SignalStatus.OK, value=1.5, reasons=[], details={}, latency_ms=1.0)]
    session.add_all([e, scan])
    with pytest.raises(IntegrityError):
        session.flush()


def test_unknown_verdict_rejected_by_db(session):
    e = make_email()
    session.add(e)
    session.flush()
    with pytest.raises(IntegrityError):
        session.execute(text(
            "insert into scan_results (id, email_id, score, verdict, action, remediations, reasons,"
            " unavailable, abstained, config_version, scanned_at, latency_ms) values"
            " (:id, :e, 10, 'malicious', 'deliver', '[]', '[]', '[]', '[]', 'd', now(), 1)"
        ), {"id": uuid.uuid4(), "e": e.id})


def test_deleting_email_cascades(session):
    e = make_email()
    scan = make_scan(e.id)
    scan.signals = [SignalRow(module="x", status=SignalStatus.ABSTAINED, value=None, reasons=[], details={}, latency_ms=1.0)]
    session.add_all([e, scan])
    session.flush()
    session.execute(text("delete from emails where id = :i"), {"i": e.id})
    assert session.execute(text("select count(*) from signals where scan_result_id = :i"), {"i": scan.id}).scalar() == 0
