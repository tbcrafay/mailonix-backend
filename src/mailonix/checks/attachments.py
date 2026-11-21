"""Group D: attachments (WP3D). ABHI PLACEHOLDER.

Asli version (Sprint 2, cyber side), main process se alag worker mein (static, kabhi chalaya nahi jata):
- FR-5.1 khatarnak file type: extension + file signature (magic bytes), declared content_type par bharosa nahi
- FR-5.2 Office macro (oletools)
- FR-5.3 nested archive, gehrai aur size ki hadd ke saath
- FR-5.4 password wala archive = risk signal
- EICAR test file pakarna (demo)

Parhta hai: attachments[] (filename, content_type, size, sha256, stored_path)
details (tajweez): {"files": [{"filename": ..., "true_type": ..., "macro": bool, "flags": [...]}]}
config/checks.toml [attachments]: dangerous_extensions, max_archive_depth, max_unpacked_mb, ...
"""

from .base import PlaceholderCheck


class AttachmentsCheck(PlaceholderCheck):
    name = "attachments"
    group = "D"
