"""Fixtures for the ``automerge`` package tests."""

import logging

import pytest

import automerge.github

from fakes import FakeGh


@pytest.fixture(autouse=True)
def automerge_logger():
    """Drop the handler ``cli.main`` installs, so it does not carry over into other tests."""
    yield
    logger = logging.getLogger("automerge")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)


@pytest.fixture
def fake_gh(monkeypatch: pytest.MonkeyPatch):
    """Put a ``FakeGh`` in place of the real ``gh`` and hand it back."""

    def install(pulls: dict[int, dict], **kwargs) -> FakeGh:
        fake = FakeGh(pulls, **kwargs)
        monkeypatch.setattr(automerge.github.subprocess, "run", fake)
        return fake

    return install
