"""Tests for the arming rules behind the ``automerge`` composite action."""

import json
import subprocess

from pathlib import Path

import pytest
import yaml

import automerge

from automerge import Decision, decide, main, parse_numbers


ROOT = Path(__file__).resolve().parent.parent
ACTION = ROOT / ".github" / "actions" / "automerge" / "action.yml"
WORKFLOW = ROOT / ".github" / "workflows" / "shared-automerge.yml"


def dependabot_body(*entries: str, bumps: str = "") -> str:
    """A dependabot commit body: the prose, then one metadata entry per dependency."""
    return (
        f"{bumps}\n"
        "- [Release notes](https://example.com/releases)\n"
        "\n"
        "---\n"
        "updated-dependencies:\n" + "".join(entries) + "...\n"
        "\n"
        "Signed-off-by: dependabot[bot] <support@github.com>"
    )


def entry(name: str, version: str, update_type: str | None = None) -> str:
    text = f"- dependency-name: {name}\n  dependency-version: {version}\n  dependency-type: direct:production\n"
    if update_type is not None:
        text += f"  update-type: version-update:{update_type}\n"
    return text


# fizyk/pyramid_fullauth#999: a security update, so no update-type.
URLLIB3_HEADLINE = "Bump urllib3 from 2.7.0 to 2.8.0"
URLLIB3_BODY = """\
Bumps [urllib3](https://github.com/urllib3/urllib3) from 2.7.0 to 2.8.0.
- [Release notes](https://github.com/urllib3/urllib3/releases)
- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)
- [Commits](https://github.com/urllib3/urllib3/compare/2.7.0...2.8.0)

---
updated-dependencies:
- dependency-name: urllib3
  dependency-version: 2.8.0
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/pyramid_fullauth#1000: a security update fixing an advisory with a major bump.
OAUTHLIB_HEADLINE = "Bump oauthlib from 3.3.1 to 4.0.0"
OAUTHLIB_BODY = """\
Bumps [oauthlib](https://github.com/oauthlib/oauthlib) from 3.3.1 to 4.0.0.
- [Release notes](https://github.com/oauthlib/oauthlib/releases)
- [Changelog](https://github.com/oauthlib/oauthlib/blob/master/CHANGELOG.rst)
- [Commits](https://github.com/oauthlib/oauthlib/compare/v3.3.1...v4.0.0)

---
updated-dependencies:
- dependency-name: oauthlib
  dependency-version: 4.0.0
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/actions-reuse#370: a pre-commit hook, named by URL, so the headline is cut short.
ZIZMOR_HEADLINE = "Bump https://github.com/zizmorcore/zizmor-pre-commit"
ZIZMOR_BODY = """\
Bumps [https://github.com/zizmorcore/zizmor-pre-commit](https://github.com/zizmorcore/zizmor-pre-commit) \
from v1.30.0 to 1.30.1.
- [Release notes](https://github.com/zizmorcore/zizmor-pre-commit/releases)
- [Commits](https://github.com/zizmorcore/zizmor-pre-commit/compare/v1.30.0...v1.30.1)

---
updated-dependencies:
- dependency-name: https://github.com/zizmorcore/zizmor-pre-commit
  dependency-version: 1.30.1
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/actions-reuse#392: one grouped action bump across four directories.
SETUP_UV_HEADLINE = "Bump the setup-uv group across 4 directories with 1 update"
SETUP_UV_BODY = (
    "Bumps the setup-uv group with 1 update in the / directory: "
    "[astral-sh/setup-uv](https://github.com/astral-sh/setup-uv).\n"
    "\n"
    "Updates `astral-sh/setup-uv` from 10.2.0 to 10.3.0\n"
    "\n"
    "---\n"
    "updated-dependencies:\n"
    + "".join(
        "- dependency-name: astral-sh/setup-uv\n"
        "  dependency-version: 10.3.0\n"
        "  dependency-type: direct:production\n"
        "  update-type: version-update:semver-minor\n"
        "  dependency-group: setup-uv\n"
        for _ in range(4)
    )
    + "...\n\nSigned-off-by: dependabot[bot] <support@github.com>"
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
def test_dependabot(headline: str, body: str, arm: bool) -> None:
    assert decide("app/dependabot", headline, body).arm is arm


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
        ("Bump x", "", "has no update type and no versions to compare, skipping."),
    ],
)
def test_dependabot_reason(headline: str, body: str, reason: str) -> None:
    """The versions are read without their ``v`` and without a directory suffix."""
    assert decide("app/dependabot", headline, body).reason == reason


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
def test_renovate(body: str, decision: Decision) -> None:
    """The last ``Update-Type`` trailer counts, and it has to start its line."""
    assert decide("app/renovate", "Update dependency @mermaid-js/mermaid-cli to v12", body) == decision


def test_pre_commit_ci() -> None:
    assert decide("app/pre-commit-ci", "[pre-commit.ci] pre-commit autoupdate", "").arm is True


@pytest.mark.parametrize("author", ["fizyk", "app/github-actions", "dependabot", "renovate[bot]"])
def test_other_authors(author: str) -> None:
    assert decide(author, URLLIB3_HEADLINE, URLLIB3_BODY) == Decision(False, f"was created by {author}, skipping.")


@pytest.mark.parametrize(
    ("spec", "numbers"),
    [
        ("", []),
        ("null", []),
        ("[]", []),
        ("42", [42]),
        ("42 43\n44", [42, 43, 44]),
        ('[{"number": 42, "head": {}}, {"number": 43}]', [42, 43]),
        ("[42, 43]", [42, 43]),
    ],
)
def test_parse_numbers(spec: str, numbers: list[int]) -> None:
    assert parse_numbers(spec) == numbers


# main(), with gh standing in.


class FakeGh:
    """Answers ``gh pr view`` from a table and records every other call."""

    def __init__(self, pulls: dict[int, dict], fail: tuple[str, ...] = ()) -> None:
        self.pulls = pulls
        self.fail = fail
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args, check, capture_output, text):
        assert args[0] == "gh" and check and capture_output and text
        args = tuple(args[1:])
        if args[:2] == ("pr", "view"):
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(self.pulls[int(args[2])]), stderr="")
        self.calls.append(args)
        if args[:2] == self.fail:
            raise subprocess.CalledProcessError(1, ("gh", *args), stderr="GraphQL: nope\n")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def pull(
    author: str = "app/dependabot",
    headline: str = URLLIB3_HEADLINE,
    body: str = URLLIB3_BODY,
    state: str = "OPEN",
    reviews: tuple[str, ...] = (),
    armed: bool = False,
    head: str = "abc123",
) -> dict:
    return {
        "author": {"login": author},
        "state": state,
        "commits": [
            {"messageHeadline": "an older commit", "messageBody": ""},
            {"messageHeadline": headline, "messageBody": body},
        ],
        "reviews": [{"state": review} for review in reviews],
        "autoMergeRequest": {"enabledAt": "2026-10-16T00:00:00Z"} if armed else None,
        "headRefOid": head,
    }


@pytest.fixture
def fake_gh(monkeypatch: pytest.MonkeyPatch):
    def install(pulls: dict[int, dict], **kwargs) -> FakeGh:
        fake = FakeGh(pulls, **kwargs)
        monkeypatch.setattr(automerge.subprocess, "run", fake)
        return fake

    return install


def test_main_approves_and_arms(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(head="deadbeef")})
    assert main([7]) == 0
    assert gh.calls == [
        ("pr", "review", "--approve", "7"),
        ("pr", "merge", "--auto", "--merge", "--match-head-commit", "deadbeef", "7"),
    ]
    out = capsys.readouterr().out
    assert "Pull request #7 bumps 2.7.0 to 2.8.0, not a major version bump." in out
    assert "Enabling auto-merge for pull request #7 by app/dependabot." in out


def test_main_reads_the_latest_commit(fake_gh) -> None:
    pulls = pull()
    pulls["commits"].reverse()
    gh = fake_gh({7: pulls})
    assert main([7]) == 0
    assert gh.calls == []


def test_main_skips_what_decide_skips(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(headline=OAUTHLIB_HEADLINE, body=OAUTHLIB_BODY)})
    assert main([7]) == 0
    assert gh.calls == []
    assert "Pull request #7 bumps 3.3.1 to 4.0.0, a major version bump, skipping." in capsys.readouterr().out


@pytest.mark.parametrize("state", ["CLOSED", "MERGED"])
def test_main_skips_pull_requests_that_are_not_open(fake_gh, capsys, state: str) -> None:
    gh = fake_gh({7: pull(state=state)})
    assert main([7]) == 0
    assert gh.calls == []
    assert f"Pull request #7 is not open: {state}." in capsys.readouterr().out


def test_main_approves_only_once(fake_gh) -> None:
    gh = fake_gh({7: pull(reviews=("COMMENTED", "APPROVED"))})
    assert main([7]) == 0
    assert gh.calls == [("pr", "merge", "--auto", "--merge", "--match-head-commit", "abc123", "7")]


def test_main_approves_after_other_reviews(fake_gh) -> None:
    gh = fake_gh({7: pull(reviews=("COMMENTED", "CHANGES_REQUESTED"))})
    assert main([7]) == 0
    assert gh.calls[0] == ("pr", "review", "--approve", "7")


def test_main_does_not_rearm(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(reviews=("APPROVED",), armed=True)})
    assert main([7]) == 0
    assert gh.calls == []
    assert "Pull request #7 already has auto-merge enabled." in capsys.readouterr().out


def test_main_approves_an_armed_pull_request(fake_gh) -> None:
    """A dismissed approval comes back even when auto-merge stayed armed."""
    gh = fake_gh({7: pull(armed=True)})
    assert main([7]) == 0
    assert gh.calls == [("pr", "review", "--approve", "7")]


def test_main_handles_several_pull_requests(fake_gh) -> None:
    gh = fake_gh({7: pull(author="fizyk"), 8: pull(author="app/pre-commit-ci", headline="x", body="")})
    assert main([7, 8]) == 0
    assert [call[-1] for call in gh.calls] == ["8", "8"]


def test_main_without_commits(fake_gh) -> None:
    pulls = pull()
    pulls["commits"] = []
    gh = fake_gh({7: pulls})
    assert main([7]) == 0
    assert gh.calls == []


def test_main_reads_the_environment(fake_gh, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PULL_REQUESTS", '[{"number": 7}]')
    gh = fake_gh({7: pull()})
    assert main() == 0
    assert len(gh.calls) == 2


def test_main_fails_when_gh_fails(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(), 8: pull()}, fail=("pr", "merge"))
    assert main([7, 8]) == 1
    assert gh.calls[-1][-1] == "7"
    out = capsys.readouterr().out
    assert "::error::gh pr merge --auto --merge --match-head-commit abc123 7 failed: GraphQL: nope" in out


# The wiring between the workflow, the action and this suite.


def test_the_script_ships_next_to_the_action() -> None:
    """``$GITHUB_ACTION_PATH`` is what makes the script reachable at all."""
    assert Path(automerge.__file__).resolve().parent == ACTION.parent
    (step,) = [step for step in yaml.safe_load(ACTION.read_text())["runs"]["steps"] if "run" in step]
    assert '"$GITHUB_ACTION_PATH/automerge.py"' in step["run"]


def test_the_workflow_calls_the_action() -> None:
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["merge-me"]["steps"]
    (step,) = [step for step in steps if "automerge" in step.get("uses", "")]
    assert step["uses"] == "$/.github/actions/automerge"
    assert set(step["with"]) == {"github-token", "pull-requests"}


def test_the_suite_runs_on_the_python_the_action_uses() -> None:
    action = yaml.safe_load(ACTION.read_text())
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "tests.yml").read_text())
    tested = json.loads(workflow["jobs"]["pytest"]["with"]["python-versions"])
    assert tested == [action["inputs"]["python-version"]["default"]]
