"""Made-up inputs: dependabot commit bodies and ``gh pr view`` answers."""

from commit_messages import URLLIB3_BODY, URLLIB3_HEADLINE


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
