"""Group B: threat intelligence (WP3B). ABHI PLACEHOLDER.

Asli version (Sprint 2, cyber side):
- FR-3.1 attachment SHA-256, link domains aur connecting IP ki lookup, ek provider interface ke zariye.
  `TI_MODE=live|mock|hybrid` (.env). Mock pehle: local JSON list, deterministic.
- FR-3.2 cache (time limit ke saath), rate limit; lookup fail = `unavailable`, kabhi "safe" nahi.
- Sirf hash, domain aur IP bahar jata hai (NFR), email ka matn kabhi nahi.

Parhta hai: attachments[].sha256, links[].url, connecting_ip
details (tajweez): {"hits": [{"type": "domain", "value": ..., "source": ...}], "mode": "mock"}
config/checks.toml [threat_intel]: cache_ttl_seconds, mock_list_path, ...
"""

from .base import PlaceholderCheck


class ThreatIntelCheck(PlaceholderCheck):
    name = "threat_intel"
    group = "B"
