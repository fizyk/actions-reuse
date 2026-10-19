"""Fixtures for the ``automerge`` package tests."""

import pytest

import automerge.github

from fakes import FakeGh


@pytest.fixture
def fake_gh(monkeypatch: pytest.MonkeyPatch):
    """Put a ``FakeGh`` in place of the real ``gh`` and hand it back."""

    def install(pulls: dict[int, dict], **kwargs) -> FakeGh:
        fake = FakeGh(pulls, **kwargs)
        monkeypatch.setattr(automerge.github.subprocess, "run", fake)
        return fake

    return install
