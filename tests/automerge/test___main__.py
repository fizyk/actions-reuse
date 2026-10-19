"""Tests for ``automerge.__main__``: what ``python -m automerge`` does."""

import runpy

import pytest

from builders import pull


def test_runs_as_a_module(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty input is a successful no-op."""
    monkeypatch.setattr("sys.argv", ["automerge", "--", ""])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("automerge", run_name="__main__")
    assert exit_info.value.code == 0


def test_exits_with_mains_status(fake_gh, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_gh({7: pull()}, fail=("pr", "review"))
    monkeypatch.setattr("sys.argv", ["automerge", "7"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("automerge", run_name="__main__")
    assert exit_info.value.code == 1
