"""ParsedEmail: parser ka output, har check ka input. Contract v1.0."""

from uuid import UUID

from pydantic import AwareDatetime, Field

from .base import Contract
from .enums import AttachmentDisposition, LinkSource, ParseStatus


class HeaderField(Contract):
    """Ek header line. List mein asli tarteeb aur duplicates (maslan kai Received) mehfooz rehte hain."""

    name: str
    value: str


class Link(Contract):
    url: str                          # jaisa email mein tha, normalize nahi kiya
    anchor_text: str | None = None    # sirf HTML_HREF par; visible text vs href mismatch (FR-4.3) ke liye
    source: LinkSource


class Attachment(Contract):
    filename: str | None = None       # header mein naam na ho to None
    content_type: str                 # email ka declared type; asli type WP3D magic bytes se dekhe
    size: int = Field(ge=0)           # bytes
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    disposition: AttachmentDisposition
    stored_path: str                  # disk par bytes ki jagah (data dir ke andar). Bytes contract mein nahi.


class ParsedEmail(Contract):
    # pehchan
    email_id: UUID                    # ingestion par banta hai, DB insert se pehle bhi maujood
    message_id: str | None = None     # Message-ID header; kuch emails mein hota hi nahi
    received_at: AwareDatetime        # proxy ne kab li (UTC). Behaviour ka "ghanta" isi se.

    # SMTP envelope (SPF FR-2.1 ke liye zaroori; .eml replay mein script deti hai)
    connecting_ip: str | None = None
    helo: str | None = None
    envelope_from: str | None = None  # MAIL FROM (Return-Path). Bounce par khaali "<>" ho sakta hai -> None
    envelope_to: tuple[str, ...] = ()

    # headers se nikle hue khaas fields
    from_addr: str | None = None
    from_name: str | None = None
    reply_to: str | None = None
    to: tuple[str, ...] = ()
    cc: tuple[str, ...] = ()
    subject: str = ""
    headers: tuple[HeaderField, ...] = ()

    # body
    body_text: str | None = None      # text/plain part, ya RAW_FALLBACK par raw text
    body_html: str | None = None      # text/html part jaisa tha (sanitize nahi)
    links: tuple[Link, ...] = ()
    attachments: tuple[Attachment, ...] = ()

    # parsing ki halat (S12)
    parse_status: ParseStatus = ParseStatus.OK
    parse_defects: tuple[str, ...] = ()

    raw_path: str                     # asli .eml file ki jagah (FR-1.4)
