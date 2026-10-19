"""Real commit messages, builders for made-up ones, and a stand-in for ``gh``."""

import json
import subprocess


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
    """What ``gh pr view --json`` returns for a pull request."""
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
