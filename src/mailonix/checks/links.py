"""Group C: links aur body content (WP3C). ABHI PLACEHOLDER.

Asli version, do hisson mein:
1. Rules (Sprint 2):
   - FR-4.1 lookalike domain, typosquatting, punycode
   - FR-4.2 raw-IP link, risky TLD list
   - FR-4.3 link ka dikhne wala text aur asal href alag
   - FR-4.4 zero-width, control aur homoglyph characters
2. URL ML model (Should, baad mein): FR-4.6, lexical features + chhota tree model. Model ki file
   shuru mein load; model na ho to sirf rules (Plan B).

Parhta hai: links[] (url, anchor_text, source), body_text, body_html
details (tajweez): {"flagged_links": [{"url": ..., "rules": [...], "model_score": ...}]}
config/checks.toml [links]: risky_tlds, lookalike_threshold, model_path, ...
"""

from .base import PlaceholderCheck


class LinksCheck(PlaceholderCheck):
    name = "links"
    group = "C"
