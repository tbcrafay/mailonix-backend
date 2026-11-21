"""Group A: header aur sender ki jaanch (WP3A).

Abhi (Gate 1): sirf ek asli qaida, From aur Reply-To ke domain ka farq (SRS FR-2.4 ka hissa).

Asli version (Sprint 2, cyber side) isi file mein judega:
- FR-2.1 SPF: `connecting_ip` + `envelope_from` ka domain. IP na ho to SPF abstain, fail nahi.
- FR-2.2 DKIM: `headers` mein DKIM-Signature, raw email `raw_path` se.
- FR-2.3 DMARC + alignment: From domain vs SPF/DKIM domain (organizational domain, public suffix list).
- FR-2.4 Return-Path (`envelope_from`) mismatch bhi.
- FR-2.5 Display name spoof: `from_name` executive list se milta ho aur address nahi.
Har qaide ki value aur list config/checks.toml ke [header_auth] mein rahegi.

Parhta hai: from_addr, reply_to (aage: connecting_ip, envelope_from, from_name, headers, raw_path)
details: {"from_domain", "reply_to_domain"} (aage: "spf", "dkim", "dmarc" ke nateeje)
"""

from mailonix.contracts import ParsedEmail, Signal

from .base import Check, reason


def _domain(address: str | None) -> str | None:
    if not address or "@" not in address:
        return None
    return address.rsplit("@", 1)[1].strip().strip(">").lower() or None


class HeaderAuthCheck(Check):
    name = "header_auth"
    group = "A"
    default_params = {
        # Reply-To ka domain From se alag ho to kitna shak (0..1). Bohat si jaiz emails mein bhi
        # hota hai (newsletters, support desk), is liye pakka khatra nahi.
        "reply_to_mismatch_value": 0.6,
    }

    async def run(self, email: ParsedEmail) -> Signal:
        from_domain = _domain(email.from_addr)
        if from_domain is None:
            return self.abstain("no_from_address", "From address nahi mila, jaanch nahi ho sakti")

        reply_domain = _domain(email.reply_to)
        details = {"from_domain": from_domain, "reply_to_domain": reply_domain}

        # Abhi exact domain ka muqabla; subdomain/organizational domain DMARC alignment ke saath (WP3A).
        if reply_domain is not None and reply_domain != from_domain:
            return self.ok(
                self.params["reply_to_mismatch_value"],
                [reason("reply_to_mismatch",
                        f"Reply-To ({reply_domain}) From ({from_domain}) ke domain se alag hai")],
                details,
            )
        return self.ok(0.0, details=details)
