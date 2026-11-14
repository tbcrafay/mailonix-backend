"""Mailonix ke saare frozen enums. Contract v1.0.

Qaida: yahan koi value badalni ya hatani ho to pehle Rafay se poocho.
Nayi value add karna bhi contract change hai (DB aur frontend dono par asar).
Values hamesha lowercase snake_case strings hain; UI unhein jaise chahe dikhaye
(maslan verdict "high" ko "HIGH").
"""

from enum import StrEnum


class SignalStatus(StrEnum):
    """Ek check ka nateeja kis halat mein aaya."""

    OK = "ok"                    # check chala, value 0..1 maujood
    UNAVAILABLE = "unavailable"  # check chal hi nahi saka (error / timeout). Kabhi "safe" nahi.
    ABSTAINED = "abstained"      # check chala, lekin data kam tha, raye nahi di


class Verdict(StrEnum):
    """SRS FR-8.4: score -> threshold table -> verdict."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNSCANNED = "unscanned"      # FR-8.9: poora scan fail ya timeout; score nahi hota


class Disposition(StrEnum):
    """Email ke saath aakhir mein kya hua (frontend: Delivered / Quarantined / Blocked)."""

    DELIVER = "deliver"          # inbox tak gayi (remediation ke saath ya baghair)
    QUARANTINE = "quarantine"    # rok li gayi, analyst release kar sakta hai
    BLOCK = "block"              # SMTP par hi wapas kar di gayi (default policy mein istemal nahi)


class Remediation(StrEnum):
    """SRS FR-8.5 / FR-8.6 / FR-8.9: deliver se pehle email par kya tabdeeli lagi. Kai ek saath lag sakti hain."""

    BANNER = "banner"
    STRIP_LINKS = "strip_links"
    ISOLATE_ATTACHMENT = "isolate_attachment"
    UNSCANNED_BANNER = "unscanned_banner"


class ParseStatus(StrEnum):
    """S12: parser kabhi crash nahi karta; bigri email par yeh batata hai ke kitna bhar saka."""

    OK = "ok"
    PARTIAL = "partial"            # kuch hissay (maslan ek MIME part) parh nahi sake
    RAW_FALLBACK = "raw_fallback"  # MIME toot gaya, body_text mein sirf raw text hai


class LinkSource(StrEnum):
    """Link email mein kahan se mila."""

    HTML_HREF = "html_href"  # <a href="..."> se (anchor_text maujood)
    TEXT = "text"            # plain text mein likha hua URL


class AttachmentDisposition(StrEnum):
    ATTACHMENT = "attachment"
    INLINE = "inline"


class UserRole(StrEnum):
    """users table ke liye (portal roles)."""

    ADMIN = "admin"
    ANALYST = "analyst"
