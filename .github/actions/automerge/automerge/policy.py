"""Which author gets judged by which rules."""

from automerge import dependabot, renovate
from automerge.decision import Decision

DEPENDABOT = "app/dependabot"
RENOVATE = "app/renovate"
PRE_COMMIT_CI = "app/pre-commit-ci"


def decide(author: str, headline: str, body: str) -> Decision:
    """Judge a pull request by its author and the message of its latest commit.

    Pure: everything it needs is an argument, so every rule is testable against real
    commit messages without a pull request or a token.
    """
    if author == DEPENDABOT:
        return dependabot.decide(headline, body)
    if author == RENOVATE:
        return renovate.decide(body)
    if author == PRE_COMMIT_CI:
        return Decision(True, "was created by pre-commit.ci.")
    return Decision(False, f"was created by {author}, skipping.")
