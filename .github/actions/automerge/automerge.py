"""Arm GitHub's native auto-merge on dependency update pull requests.

Arms auto-merge rather than merging immediately. Merging immediately races external
checks that report through the Statuses API (pre-commit.ci): those land after the last
``workflow_run`` or ``check_suite`` event fires, so the merge is rejected for a pending
required check and nothing triggers a retry. Auto-merge is declarative - GitHub
performs the merge once the final required check reports, whichever API it arrives
through.

Only dependabot, renovate and pre-commit.ci pull requests are armed, and of those only
updates known not to be major version bumps. Requires ``allow_auto_merge`` to be
enabled on the calling repository.

Standard library only: the action runs it without installing anything.
"""

import dataclasses
import json
import os
import re
import subprocess
import sys

from collections.abc import Iterable

DEPENDABOT = "app/dependabot"
RENOVATE = "app/renovate"
PRE_COMMIT_CI = "app/pre-commit-ci"

ALLOWED_DEPENDABOT_TYPES = frozenset({"version-update:semver-minor", "version-update:semver-patch"})
ALLOWED_RENOVATE_TYPES = frozenset({"minor", "patch", "digest", "pin", "pinDigest", "lockFileMaintenance"})

VERSION = r"v?([0-9]+(?:\.[0-9]+)*)"
# `Bump <name> from <old> to <new>[ in <directory>]`
HEADLINE_RE = re.compile(rf"Bump .+ from {VERSION} to {VERSION}(?: in .+)?")
# `Bumps [<name>](<url>) from <old> to <new>.`
BUMPS_RE = re.compile(rf"Bumps \[[^]]+\]\([^)]+\) from {VERSION} to {VERSION}\.")
DEPENDENCY_RE = re.compile(r"^- dependency-name:", re.MULTILINE)
UPDATE_TYPE_RE = re.compile(r"version-update:[a-z-]*")
RENOVATE_TYPE_RE = re.compile(r"^Update-Type: (.*)$", re.MULTILINE)


@dataclasses.dataclass(frozen=True)
class Decision:
    """Whether to arm a pull request, and why, phrased to follow ``Pull request #N``."""

    arm: bool
    reason: str


def decide(author: str, headline: str, body: str) -> Decision:
    """Judge a pull request by its author and the message of its latest commit.

    Pure: everything it needs is an argument, so every rule is testable against real
    commit messages without a pull request or a token.
    """
    if author == DEPENDABOT:
        return decide_dependabot(headline, body)
    if author == RENOVATE:
        return decide_renovate(body)
    if author == PRE_COMMIT_CI:
        return Decision(True, "was created by pre-commit.ci.")
    return Decision(False, f"was created by {author}, skipping.")


def decide_dependabot(headline: str, body: str) -> Decision:
    """Equivalent of merge-me-action's DEPENDABOT_MINOR preset.

    Read from the metadata dependabot writes into the commit message rather than parsed
    out of the pull request title. Only update types known not to be majors are armed.
    """
    dependencies = len(DEPENDENCY_RE.findall(body))
    if "version-update:" in body:
        # A grouped update lists one entry per dependency, so every entry has to be a
        # minor or patch: one major among them, or an entry without an update type,
        # skips the whole pull request.
        update_types = UPDATE_TYPE_RE.findall(body)
        if not ALLOWED_DEPENDABOT_TYPES.issuperset(update_types) or len(update_types) != dependencies:
            return Decision(False, "is not solely minor or patch version bumps, skipping.")
        return Decision(True, "is solely minor or patch version bumps.")

    # Dependabot leaves `update-type` out of security updates and pre-commit updates,
    # so fall back to the versions in the commit headline. A long dependency name
    # (pre-commit names hooks by their repository URL) gets the headline cut down to
    # `Bump <name>`, so then read the versions from the body's `Bumps` line instead.
    # Anything that does not read cleanly as a single dependency moving between plain
    # dotted versions is skipped, so a major bump fixing an advisory cannot slip through.
    versions = read_versions(headline, body) if dependencies == 1 else None
    if versions is None:
        return Decision(False, "has no update type and no versions to compare, skipping.")
    old, new = versions
    if is_major_bump(old, new):
        return Decision(False, f"bumps {old} to {new}, a major version bump, skipping.")
    return Decision(True, f"bumps {old} to {new}, not a major version bump.")


def read_versions(headline: str, body: str) -> tuple[str, str] | None:
    """The old and new versions of a single-dependency bump, without any ``v`` prefix."""
    match = HEADLINE_RE.fullmatch(headline)
    if match is None:
        bumps = next((line for line in body.splitlines() if line.startswith("Bumps ")), "")
        match = BUMPS_RE.fullmatch(bumps)
    if match is None:
        return None
    return match.group(1), match.group(2)


def is_major_bump(old: str, new: str) -> bool:
    """Whether the major version moves - or, before 1.0, the minor version, the breaking one there."""
    old_major, old_minor = _major_minor(old)
    new_major, new_minor = _major_minor(new)
    return old_major != new_major or (old_major == 0 and old_minor != new_minor)


def _major_minor(version: str) -> tuple[int, int]:
    parts = [int(part) for part in version.split(".")]
    return parts[0], parts[1] if len(parts) > 1 else 0


def decide_renovate(body: str) -> Decision:
    """Arm only update types known not to be majors.

    Renovate writes no update metadata of its own, so the calling repository's renovate
    config has to add it with ``"commitBody": "Update-Type: {{updateType}}"``. Requiring
    a known type also skips pull requests missing the trailer.
    """
    trailers = RENOVATE_TYPE_RE.findall(body)
    update_type = trailers[-1] if trailers else ""
    if update_type in ALLOWED_RENOVATE_TYPES:
        return Decision(True, f"is a '{update_type}' update.")
    return Decision(False, f"is a '{update_type or 'unknown'}' update, skipping.")


def parse_numbers(spec: str) -> list[int]:
    """Read pull request numbers out of the action's input.

    ``pull_request_target`` carries a single pull request directly; the continuous
    integration events carry a JSON list of the pull requests the finished run belonged
    to. Plain whitespace-separated numbers are accepted as well.
    """
    spec = spec.strip()
    try:
        value = json.loads(spec) if spec else None
    except json.JSONDecodeError:
        return [int(part) for part in spec.split()]
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    return [int(item["number"] if isinstance(item, dict) else item) for item in value]


def gh(*args: str) -> str:
    """Run gh and return its stdout. A failure fails the run, as ``set -e`` did."""
    return subprocess.run(("gh", *args), check=True, capture_output=True, text=True).stdout


def process(number: int) -> None:
    """Approve and arm one pull request, when its author and update type allow."""
    information = json.loads(
        gh("pr", "view", str(number), "--json", "author,state,commits,reviews,autoMergeRequest,headRefOid")
    )
    author = information["author"]["login"]
    state = information["state"]
    commit = information["commits"][-1] if information["commits"] else {}

    if state != "OPEN":
        print(f"Pull request #{number} is not open: {state}.")
        return

    decision = decide(author, commit.get("messageHeadline") or "", commit.get("messageBody") or "")
    print(f"Pull request #{number} {decision.reason}")
    if not decision.arm:
        return

    # Approve only when nothing has approved yet, mirroring merge-me-action's
    # `reviews(last: 1, states: APPROVED)` check. Without this a repository requiring
    # approvals would arm auto-merge and then wait forever, since nothing else reviews
    # dependabot, renovate and pre-commit.ci pull requests.
    if not any(review["state"] == "APPROVED" for review in information["reviews"]):
        print(f"Approving pull request #{number}.")
        gh("pr", "review", "--approve", str(number))

    # `synchronize` fires on every dependabot rebase, so an already armed pull request
    # comes back around routinely, and `gh pr merge` passes any error from
    # `enablePullRequestAutoMerge` straight through.
    if information["autoMergeRequest"] is not None:
        print(f"Pull request #{number} already has auto-merge enabled.")
        return

    # The gates above were evaluated against the head read here, so pin the arming to
    # it: dependabot force-pushes on rebase, and without this a push landing between
    # the read and the call would arm a commit that was never gated.
    print(f"Enabling auto-merge for pull request #{number} by {author}.")
    gh("pr", "merge", "--auto", "--merge", "--match-head-commit", information["headRefOid"], str(number))


def main(numbers: Iterable[int] | None = None) -> int:
    if numbers is None:
        numbers = parse_numbers(os.environ.get("PULL_REQUESTS", ""))
    try:
        for number in numbers:
            process(number)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip() or f"exit status {error.returncode}"
        print(f"::error::{' '.join(error.cmd)} failed: {detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
