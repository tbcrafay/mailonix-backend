"""Core tables (Gate 1): users, emails, scan_results, signals.

Gateway aur API (WP6) dono yahi models istemal karte hain.
Naya table ya column: pehle tech lead se baat, phir ek hi banda migration banaye.

Enums database mein VARCHAR + CHECK constraint ki shakal mein jate hain (Postgres ka native
ENUM type nahi), taake baad mein enum mein value add karna sirf ek chhoti migration ho.
Values wahi lowercase strings hain jo contracts/enums.py mein hain.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    MetaData,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from mailonix.contracts.enums import Disposition, ParseStatus, SignalStatus, UserRole, Verdict

# Constraint ke naam fixed pattern par, taake har machine par migration ek jaisi bane.
NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


def str_enum(enum_cls: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda e: [m.value for m in e],
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(str_enum(UserRole, "user_role"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Email(Base):
    __tablename__ = "emails"

    # Wohi UUID jo ParsedEmail.email_id mein hai (ingestion par banta hai)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    message_id: Mapped[str | None] = mapped_column(Text)
    envelope_from: Mapped[str | None] = mapped_column(String(320))
    from_addr: Mapped[str | None] = mapped_column(String(320))
    recipients: Mapped[list[str]] = mapped_column(JSONB, default=list)  # envelope_to, list
    subject: Mapped[str] = mapped_column(Text, default="")
    connecting_ip: Mapped[str | None] = mapped_column(String(45))  # IPv6 tak
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    parse_status: Mapped[ParseStatus] = mapped_column(str_enum(ParseStatus, "parse_status"))
    raw_path: Mapped[str] = mapped_column(Text)

    scan_results: Mapped[list["ScanResultRow"]] = relationship(back_populates="email")

    __table_args__ = (
        Index("ix_emails_received_at", "received_at"),
        Index("ix_emails_from_addr", "from_addr"),
    )


class ScanResultRow(Base):
    """Ek email ke kai scans ho sakte hain (maslan dobara replay), is liye email_id unique nahi."""

    __tablename__ = "scan_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("emails.id", ondelete="CASCADE"))
    score: Mapped[float | None] = mapped_column(Float)
    verdict: Mapped[Verdict] = mapped_column(str_enum(Verdict, "verdict"))
    action: Mapped[Disposition] = mapped_column(str_enum(Disposition, "disposition"))
    remediations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    unavailable: Mapped[list[str]] = mapped_column(JSONB, default=list)
    abstained: Mapped[list[str]] = mapped_column(JSONB, default=list)
    config_version: Mapped[str] = mapped_column(String(64))
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[float] = mapped_column(Float)

    email: Mapped[Email] = relationship(back_populates="scan_results")
    signals: Mapped[list["SignalRow"]] = relationship(
        back_populates="scan_result", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 100)", name="score_range"),
        CheckConstraint("(verdict = 'unscanned') = (score IS NULL)", name="score_matches_verdict"),
        Index("ix_scan_results_email_id", "email_id"),
        Index("ix_scan_results_scanned_at", "scanned_at"),
        Index("ix_scan_results_verdict", "verdict"),
    )


class SignalRow(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    scan_result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scan_results.id", ondelete="CASCADE")
    )
    module: Mapped[str] = mapped_column(String(64))
    status: Mapped[SignalStatus] = mapped_column(str_enum(SignalStatus, "signal_status"))
    value: Mapped[float | None] = mapped_column(Float)
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    latency_ms: Mapped[float] = mapped_column(Float)

    scan_result: Mapped[ScanResultRow] = relationship(back_populates="signals")

    __table_args__ = (
        CheckConstraint("value IS NULL OR (value >= 0 AND value <= 1)", name="value_range"),
        CheckConstraint("(status = 'ok') = (value IS NOT NULL)", name="value_matches_status"),
        Index("ix_signals_scan_result_id", "scan_result_id"),
        Index("ix_signals_module", "module"),
    )
