"""Renovate: arm only update types known not to be majors.

Renovate writes no update metadata of its own, so the calling repository's renovate
config has to add it with ``"commitBody": "Update-Type: {{updateType}}"``. Requiring a
known type also skips pull requests missing the trailer.
"""

import re

from automerge.decision import Decision

ALLOWED_TYPES = frozenset({"minor", "patch", "digest", "pin", "pinDigest", "lockFileMaintenance"})

UPDATE_TYPE_RE = re.compile(r"^Update-Type: (.*)$", re.MULTILINE)


def decide(body: str) -> Decision:
    """Judge a renovate pull request by the last ``Update-Type`` trailer of its commit."""
    trailers = UPDATE_TYPE_RE.findall(body)
    update_type = trailers[-1] if trailers else ""
    if update_type in ALLOWED_TYPES:
        return Decision(True, f"is a '{update_type}' update.")
    return Decision(False, f"is a '{update_type or 'unknown'}' update, skipping.")
