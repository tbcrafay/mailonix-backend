"""Group E: behaviour baseline (WP3E, Must). ABHI PLACEHOLDER.

Asli version (Sprint 2):
- FR-6.1 har sender-recipient joday ki ginti aur ghante ka histogram (DB se PARHTA hai, likhta nahi;
  baseline update orchestrator karega, sirf kam khatre wali emails se, FR-6.3)
- FR-6.2 naya joda, ajeeb ghanta
- Kam history ho to `abstained` (S13 pass line: injected anomalies par AUC >= 0.70)

Parhta hai: from_addr, envelope_to, received_at (+ DB ki baseline table, WP6 mein banegi)
details (tajweez): {"pair_count": n, "first_time_pair": bool, "hour": h, "hour_rarity": 0..1}
config/checks.toml [behaviour]: min_history, off_hours_threshold, ...
"""

from .base import PlaceholderCheck


class BehaviourCheck(PlaceholderCheck):
    name = "behaviour"
    group = "E"
