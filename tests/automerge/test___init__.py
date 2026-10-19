"""Tests for ``automerge``: what the package exposes."""

import automerge

from automerge import cli, decision, policy


def test_exports() -> None:
    """The package re-exports the pieces the action and the suite reach for."""
    assert automerge.Decision is decision.Decision
    assert automerge.decide is policy.decide
    assert automerge.main is cli.main
    assert automerge.parse_args is cli.parse_args
    assert automerge.parse_numbers is cli.parse_numbers
    assert automerge.process is cli.process
    assert sorted(automerge.__all__) == ["Decision", "decide", "main", "parse_args", "parse_numbers", "process"]
