"""The ``gh`` calls, authenticated by ``GH_TOKEN`` and aimed by ``GH_REPO``."""

import json
import subprocess


def gh(*args: str) -> str:
    """Run gh and return its stdout. A failure raises ``CalledProcessError``."""
    return subprocess.run(("gh", *args), check=True, capture_output=True, text=True).stdout


def view(number: int) -> dict:
    """What arming a pull request depends on, read in one call."""
    return json.loads(gh("pr", "view", str(number), "--json", "author,state,commits,reviews,autoMergeRequest,headRefOid"))


def approve(number: int) -> None:
    gh("pr", "review", "--approve", str(number))


def arm(number: int, head: str) -> None:
    """Enable auto-merge, pinned to *head* so a push landing since it was read is not armed."""
    gh("pr", "merge", "--auto", "--merge", "--match-head-commit", head, str(number))
