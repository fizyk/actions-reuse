"""Tests for ``automerge.dependabot``, against real commit messages where there are some."""

import pytest

from automerge.dependabot import decide, is_major_bump, read_versions
from builders import dependabot_body, entry
from commit_messages import (
    OAUTHLIB_BODY,
    OAUTHLIB_HEADLINE,
    SETUP_UV_BODY,
    SETUP_UV_HEADLINE,
    URLLIB3_BODY,
    URLLIB3_HEADLINE,
    ZIZMOR_BODY,
    ZIZMOR_HEADLINE,
)


@pytest.mark.parametrize(
    ("headline", "body", "arm"),
    [
        pytest.param(
            "Bump pytest from 9.1.0 to 9.1.1",
            dependabot_body(entry("pytest", "9.1.1", "semver-patch")),
            True,
            id="semver-patch",
        ),
        pytest.param(
            "Bump pytest from 9.0.0 to 9.1.0",
            dependabot_body(entry("pytest", "9.1.0", "semver-minor")),
            True,
            id="semver-minor",
        ),
        pytest.param(
            "Bump pytest from 8.4.0 to 9.0.0",
            dependabot_body(entry("pytest", "9.0.0", "semver-major")),
            False,
            id="semver-major",
        ),
        pytest.param(SETUP_UV_HEADLINE, SETUP_UV_BODY, True, id="grouped-minor"),
        pytest.param(
            "Bump the python group with 2 updates",
            dependabot_body(entry("pytest", "9.1.1", "semver-patch"), entry("towncrier", "27.0.0", "semver-major")),
            False,
            id="grouped-with-a-major",
        ),
        pytest.param(
            "Bump the python group with 2 updates",
            dependabot_body(entry("pytest", "9.1.1", "semver-patch"), entry("urllib3", "2.8.0")),
            False,
            id="grouped-with-an-entry-missing-its-update-type",
        ),
        pytest.param(URLLIB3_HEADLINE, URLLIB3_BODY, True, id="security-minor"),
        pytest.param(OAUTHLIB_HEADLINE, OAUTHLIB_BODY, False, id="security-major"),
        pytest.param(
            "Bump left-pad from 0.1.0 to 0.2.0", dependabot_body(entry("left-pad", "0.2.0")), False, id="security-0.x-minor"
        ),
        pytest.param(
            "Bump left-pad from 0.1.0 to 0.1.1", dependabot_body(entry("left-pad", "0.1.1")), True, id="security-0.x-patch"
        ),
        pytest.param("Bump left-pad from 1 to 2", dependabot_body(entry("left-pad", "2")), False, id="security-bare-major"),
        pytest.param("Bump left-pad from 1 to 1.1", dependabot_body(entry("left-pad", "1.1")), True, id="security-bare-minor"),
        pytest.param(
            "Bump https://github.com/tox-dev/pyproject-fmt from v0.16.7 to 0.16.8",
            dependabot_body(entry("https://github.com/tox-dev/pyproject-fmt", "0.16.8")),
            True,
            id="pre-commit-v-prefix",
        ),
        pytest.param(ZIZMOR_HEADLINE, ZIZMOR_BODY, True, id="pre-commit-shortened-headline"),
        pytest.param(
            "Bump sphinx from 8.1.0 to 8.2.0 in /docs",
            dependabot_body(entry("sphinx", "8.2.0")),
            True,
            id="directory-suffix",
        ),
        pytest.param(
            "Bump sphinx from 8.1.0 to 9.0.0 in /docs",
            dependabot_body(entry("sphinx", "9.0.0")),
            False,
            id="directory-suffix-major",
        ),
        pytest.param(
            "Bump the pip group across 1 directory with 2 updates",
            dependabot_body(entry("urllib3", "2.8.0"), entry("oauthlib", "4.0.0")),
            False,
            id="grouped-security",
        ),
        pytest.param(
            "Bump left-pad from 1.0.0 to 1.1.0rc1", dependabot_body(entry("left-pad", "1.1.0rc1")), False, id="prerelease"
        ),
        pytest.param(
            "Bump left-pad from 4d3c1b2 to 9e8f7a6",
            dependabot_body(entry("left-pad", "9e8f7a6")),
            False,
            id="git-sha",
        ),
        pytest.param(
            "Bump https://github.com/example/very-long-hook-repository-name",
            dependabot_body(entry("https://github.com/example/very-long-hook-repository-name", "abc1234")),
            False,
            id="shortened-headline-without-versions",
        ),
        pytest.param("Bump left-pad from 1.0.0 to 1.0.1", "", False, id="no-metadata"),
    ],
)
def test_decide(headline: str, body: str, arm: bool) -> None:
    assert decide(headline, body).arm is arm


@pytest.mark.parametrize(
    ("headline", "body", "reason"),
    [
        (URLLIB3_HEADLINE, URLLIB3_BODY, "bumps 2.7.0 to 2.8.0, not a major version bump."),
        (OAUTHLIB_HEADLINE, OAUTHLIB_BODY, "bumps 3.3.1 to 4.0.0, a major version bump, skipping."),
        (ZIZMOR_HEADLINE, ZIZMOR_BODY, "bumps 1.30.0 to 1.30.1, not a major version bump."),
        (
            "Bump sphinx from 8.1.0 to 8.2.0 in /docs",
            dependabot_body(entry("sphinx", "8.2.0")),
            "bumps 8.1.0 to 8.2.0, not a major version bump.",
        ),
        (SETUP_UV_HEADLINE, SETUP_UV_BODY, "is solely minor or patch version bumps."),
        (
            "Bump pytest from 8.4.0 to 9.0.0",
            dependabot_body(entry("pytest", "9.0.0", "semver-major")),
            "is not solely minor or patch version bumps, skipping.",
        ),
        ("Bump x", "", "has no update type and no versions to compare, skipping."),
    ],
)
def test_decide_reason(headline: str, body: str, reason: str) -> None:
    """The versions are read without their ``v`` and without a directory suffix."""
    assert decide(headline, body).reason == reason


@pytest.mark.parametrize(
    ("headline", "body", "versions"),
    [
        (URLLIB3_HEADLINE, URLLIB3_BODY, ("2.7.0", "2.8.0")),
        ("Bump sphinx from 8.1.0 to 8.2.0 in /docs", "", ("8.1.0", "8.2.0")),
        ("Bump hook from v0.16.7 to 0.16.8", "", ("0.16.7", "0.16.8")),
        # The headline is cut short, so the body's `Bumps` line is read instead.
        (ZIZMOR_HEADLINE, ZIZMOR_BODY, ("1.30.0", "1.30.1")),
        # Only the first `Bumps` line counts.
        ("Bump x", "Bumps [x](u) from 1.0 to 1.1.\nBumps [x](u) from 1.0 to 2.0.", ("1.0", "1.1")),
        ("Bump x from 1.0.0 to 1.1.0rc1", "", None),
        ("Bump x", "", None),
        ("Bump x", "Bumps [x](u) from 1.0 to 1.1", None),
    ],
)
def test_read_versions(headline: str, body: str, versions: tuple[str, str] | None) -> None:
    assert read_versions(headline, body) == versions


@pytest.mark.parametrize(
    ("old", "new", "major"),
    [
        ("1.2.3", "1.2.4", False),
        ("1.2.3", "1.3.0", False),
        ("1.2.3", "2.0.0", True),
        ("2.0.0", "1.9.0", True),
        ("0.1.0", "0.1.1", False),
        ("0.1.0", "0.2.0", True),
        ("0", "0.0.1", False),
        ("0", "0.1", True),
        ("1", "1.1", False),
    ],
)
def test_is_major_bump(old: str, new: str, major: bool) -> None:
    """Before 1.0 the minor version is the breaking one; a missing minor reads as 0."""
    assert is_major_bump(old, new) is major
