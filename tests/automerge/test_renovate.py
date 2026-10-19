"""Tests for ``automerge.renovate``."""

import pytest

from automerge.decision import Decision
from automerge.renovate import decide


@pytest.mark.parametrize(
    ("body", "decision"),
    [
        ("Update-Type: minor", Decision(True, "is a 'minor' update.")),
        ("Update-Type: patch", Decision(True, "is a 'patch' update.")),
        ("Update-Type: digest", Decision(True, "is a 'digest' update.")),
        ("Update-Type: pin", Decision(True, "is a 'pin' update.")),
        ("Update-Type: pinDigest", Decision(True, "is a 'pinDigest' update.")),
        ("Update-Type: lockFileMaintenance", Decision(True, "is a 'lockFileMaintenance' update.")),
        # fizyk/actions-reuse#391.
        ("Update-Type: major", Decision(False, "is a 'major' update, skipping.")),
        ("Update-Type: rollback", Decision(False, "is a 'rollback' update, skipping.")),
        ("", Decision(False, "is a 'unknown' update, skipping.")),
        ("Some prose.\n\nUpdate-Type: major\nUpdate-Type: minor", Decision(True, "is a 'minor' update.")),
        ("Update-Type: minor\nUpdate-Type: major", Decision(False, "is a 'major' update, skipping.")),
        ("  Update-Type: minor", Decision(False, "is a 'unknown' update, skipping.")),
    ],
)
def test_decide(body: str, decision: Decision) -> None:
    """The last ``Update-Type`` trailer counts, and it has to start its line."""
    assert decide(body) == decision
