"""Tests for ``automerge.policy``: which author gets judged by which rules."""

import pytest

from automerge import dependabot, renovate
from automerge.decision import Decision
from automerge.policy import decide
from commit_messages import OAUTHLIB_BODY, OAUTHLIB_HEADLINE, URLLIB3_BODY, URLLIB3_HEADLINE


@pytest.mark.parametrize(
    ("headline", "body"), [(URLLIB3_HEADLINE, URLLIB3_BODY), (OAUTHLIB_HEADLINE, OAUTHLIB_BODY)]
)
def test_dependabot_goes_to_the_dependabot_rules(headline: str, body: str) -> None:
    assert decide("app/dependabot", headline, body) == dependabot.decide(headline, body)


@pytest.mark.parametrize("body", ["Update-Type: minor", "Update-Type: major", ""])
def test_renovate_goes_to_the_renovate_rules(body: str) -> None:
    """Renovate is judged by the body alone; the headline never matters."""
    assert decide("app/renovate", "Update dependency @mermaid-js/mermaid-cli to v12", body) == renovate.decide(body)


def test_pre_commit_ci_is_always_armed() -> None:
    assert decide("app/pre-commit-ci", "[pre-commit.ci] pre-commit autoupdate", "") == Decision(
        True, "was created by pre-commit.ci."
    )


@pytest.mark.parametrize("author", ["fizyk", "app/github-actions", "dependabot", "renovate[bot]"])
def test_other_authors_are_skipped(author: str) -> None:
    """Even with a commit message any of the rules would arm."""
    assert decide(author, URLLIB3_HEADLINE, URLLIB3_BODY) == Decision(False, f"was created by {author}, skipping.")
