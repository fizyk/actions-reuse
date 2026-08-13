"""Fixtures for the release planner tests."""

import subprocess
import textwrap

from pathlib import Path

import pytest


DEFAULT_CONFIG = """\
[tool.towncrier]
directory = "newsfragments"
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(("git", *args), cwd=repo, check=True, capture_output=True)


@pytest.fixture
def make_repo(tmp_path: Path):
    """Build a repository holding a towncrier config and a set of fragment files.

    Names ending in ``/`` become directories, which is how the "a directory named
    like a fragment is not a fragment" cases are expressed.
    """

    def build(
        *names: str,
        config: str = DEFAULT_CONFIG,
        directory: str = "newsfragments",
    ) -> Path:
        (tmp_path / "towncrier.toml").write_text(textwrap.dedent(config))
        if directory:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)
        for name in names:
            target = tmp_path / directory / name.rstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith("/"):
                target.mkdir(exist_ok=True)
            else:
                target.write_text("Something happened.\n")
        return tmp_path

    return build


@pytest.fixture
def git_history():
    """Give a directory a git history: a commit, an optional tag, then more commits."""

    def build(repo: Path, tag: str | None = None, commits_after: int = 0) -> None:
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.email", "tests@example.com")
        git(repo, "config", "user.name", "tests")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "--allow-empty", "-m", "initial")
        if tag is not None:
            git(repo, "tag", tag)
        for index in range(commits_after):
            git(repo, "commit", "-q", "--allow-empty", "-m", f"work {index}")

    return build


@pytest.fixture
def outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Stand in for the step output file and the inputs GitHub passes as environment."""
    path = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(path))
    for name in ("NEWSFRAGMENTS_REQUIRED", "MINOR_FRAGMENTS", "MAJOR_FRAGMENTS"):
        monkeypatch.delenv(name, raising=False)

    def read() -> dict[str, str]:
        if not path.exists():
            return {}
        lines = path.read_text().splitlines()
        return dict(line.split("=", 1) for line in lines if line)

    return read
