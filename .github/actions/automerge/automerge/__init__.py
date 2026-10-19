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

- ``policy``: which author gets judged by which rules.
- ``dependabot``, ``renovate``: the rules themselves, pure functions of a commit message.
- ``github``: the ``gh`` calls.
- ``cli``: reads the pull request numbers from the command line and walks each pull request through the above.
"""

from automerge.cli import main, parse_args, parse_numbers, process
from automerge.decision import Decision
from automerge.policy import decide

__all__ = ["Decision", "decide", "main", "parse_args", "parse_numbers", "process"]
