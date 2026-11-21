"""Group F: intent classifier (WP3F, Must). ABHI PLACEHOLDER.

Asli version (model train hone ke baad):
- FR-7.1 har email ke liye chaar probabilities: urgency, authority, secrecy, financial request.
- Model ki file (joblib) check shuru hote hi ek dafa load; har email par predict.
- Input: subject + body_text, wohi `clean_email()` jo training (step2) mein tha.
- Model na mile ya S1 pass na ho: Plan B, lexicon scoring (`details` mein "plan": "lexicon").
- CPU par model ka hissa <= 2 s (S11).
- Ek Signal ya chaar: abhi khula; `details` mein chaaron rakhne se contract nahi tootta.

Parhta hai: subject, body_text (body_html fallback)
details (tajweez): {"urgency": p, "authority": p, "secrecy": p, "financial": p, "model": "v1"}
value (tajweez): chaaron ka max, ya config ke weights se mila hua
config/checks.toml [intent]: model_path, decision_threshold, ...
"""

from .base import PlaceholderCheck


class IntentCheck(PlaceholderCheck):
    name = "intent"
    group = "F"
