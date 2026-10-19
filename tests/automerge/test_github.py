"""Tests for ``automerge.github``: the exact ``gh`` invocations."""

import subprocess

import pytest

from automerge import github
from builders import pull


def test_view(fake_gh) -> None:
    fake_gh({7: pull(head="deadbeef")})
    assert github.view(7) == pull(head="deadbeef")


def test_view_asks_for_every_field_it_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    monkeypatch.setattr(github, "gh", lambda *args: calls.append(args) or "{}")
    github.view(7)
    assert calls == [("pr", "view", "7", "--json", "author,state,commits,reviews,autoMergeRequest,headRefOid")]


def test_approve(fake_gh) -> None:
    gh = fake_gh({})
    github.approve(7)
    assert gh.calls == [("pr", "review", "--approve", "7")]


def test_arm_pins_the_head(fake_gh) -> None:
    gh = fake_gh({})
    github.arm(7, "deadbeef")
    assert gh.calls == [("pr", "merge", "--auto", "--merge", "--match-head-commit", "deadbeef", "7")]


def test_gh_returns_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    def run(args, check, capture_output, text):
        assert args == ("gh", "api", "user") and check and capture_output and text
        return subprocess.CompletedProcess(args, 0, stdout="out", stderr="")

    monkeypatch.setattr(github.subprocess, "run", run)
    assert github.gh("api", "user") == "out"


def test_gh_raises_on_failure(fake_gh) -> None:
    fake_gh({}, fail=("pr", "review"))
    with pytest.raises(subprocess.CalledProcessError) as error:
        github.approve(7)
    assert error.value.stderr == "GraphQL: nope\n"
