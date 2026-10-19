"""Tests for ``automerge.decision``."""

import dataclasses

import pytest

from automerge.decision import Decision


def test_compares_by_value() -> None:
    assert Decision(True, "is a 'minor' update.") == Decision(True, "is a 'minor' update.")
    assert Decision(True, "x") != Decision(False, "x")


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        Decision(True, "x").arm = False  # type: ignore[misc]
