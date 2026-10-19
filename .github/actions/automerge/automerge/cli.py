"""The action's entry point: read its input and walk each pull request through."""

import json
import os
import subprocess

from collections.abc import Iterable

from automerge import github
from automerge.policy import decide


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


def process(number: int) -> None:
    """Approve and arm one pull request, when its author and update type allow."""
    information = github.view(number)
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
        github.approve(number)

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
    github.arm(number, information["headRefOid"])


def main(numbers: Iterable[int] | None = None) -> int:
    """Process every pull request; the first failing ``gh`` call fails the run, as ``set -e`` did."""
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
