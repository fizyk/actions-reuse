"""Tests for ``automerge.cli``, with ``gh`` standing in."""

import pytest

from automerge.cli import main, parse_args, parse_numbers, process
from support import OAUTHLIB_BODY, OAUTHLIB_HEADLINE, pull


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


@pytest.mark.parametrize(
    ("argv", "numbers"),
    [
        ([], []),
        ([""], []),
        (["null"], []),
        (["7", "8"], [7, 8]),
        (["7 8"], [7, 8]),
        (['[{"number": 7}, {"number": 8}]'], [7, 8]),
        (["--", "7"], [7]),
    ],
)
def test_parse_args(argv: list[str], numbers: list[int]) -> None:
    """Each argument takes any form the action's input does."""
    assert parse_args(argv) == numbers


def test_parse_args_rejects_options() -> None:
    with pytest.raises(SystemExit) as exit_info:
        parse_args(["--bogus"])
    assert exit_info.value.code == 2


# process(): one pull request.


def test_process_approves_and_arms(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(head="deadbeef")})
    process(7)
    assert gh.calls == [
        ("pr", "review", "--approve", "7"),
        ("pr", "merge", "--auto", "--merge", "--match-head-commit", "deadbeef", "7"),
    ]
    out = capsys.readouterr().out
    assert "Pull request #7 bumps 2.7.0 to 2.8.0, not a major version bump." in out
    assert "Enabling auto-merge for pull request #7 by app/dependabot." in out


def test_process_reads_the_latest_commit(fake_gh) -> None:
    pulls = pull()
    pulls["commits"].reverse()
    gh = fake_gh({7: pulls})
    process(7)
    assert gh.calls == []


def test_process_skips_what_decide_skips(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(headline=OAUTHLIB_HEADLINE, body=OAUTHLIB_BODY)})
    process(7)
    assert gh.calls == []
    assert "Pull request #7 bumps 3.3.1 to 4.0.0, a major version bump, skipping." in capsys.readouterr().out


@pytest.mark.parametrize("state", ["CLOSED", "MERGED"])
def test_process_skips_pull_requests_that_are_not_open(fake_gh, capsys, state: str) -> None:
    gh = fake_gh({7: pull(state=state)})
    process(7)
    assert gh.calls == []
    assert f"Pull request #7 is not open: {state}." in capsys.readouterr().out


def test_process_approves_only_once(fake_gh) -> None:
    gh = fake_gh({7: pull(reviews=("COMMENTED", "APPROVED"))})
    process(7)
    assert gh.calls == [("pr", "merge", "--auto", "--merge", "--match-head-commit", "abc123", "7")]


def test_process_approves_after_other_reviews(fake_gh) -> None:
    gh = fake_gh({7: pull(reviews=("COMMENTED", "CHANGES_REQUESTED"))})
    process(7)
    assert gh.calls[0] == ("pr", "review", "--approve", "7")


def test_process_does_not_rearm(fake_gh, capsys) -> None:
    gh = fake_gh({7: pull(reviews=("APPROVED",), armed=True)})
    process(7)
    assert gh.calls == []
    assert "Pull request #7 already has auto-merge enabled." in capsys.readouterr().out


def test_process_approves_an_armed_pull_request(fake_gh) -> None:
    """A dismissed approval comes back even when auto-merge stayed armed."""
    gh = fake_gh({7: pull(armed=True)})
    process(7)
    assert gh.calls == [("pr", "review", "--approve", "7")]


def test_process_without_commits(fake_gh) -> None:
    pulls = pull()
    pulls["commits"] = []
    gh = fake_gh({7: pulls})
    process(7)
    assert gh.calls == []


# main(): the command line, and every pull request on it.


def test_main_handles_several_pull_requests(fake_gh) -> None:
    gh = fake_gh({7: pull(author="fizyk"), 8: pull(author="app/pre-commit-ci", headline="x", body="")})
    assert main(["7", "8"]) == 0
    assert [call[-1] for call in gh.calls] == ["8", "8"]


def test_main_takes_the_event_payload(fake_gh) -> None:
    gh = fake_gh({7: pull()})
    assert main(['[{"number": 7, "head": {}}]']) == 0
    assert len(gh.calls) == 2


def test_main_with_nothing_to_do(fake_gh) -> None:
    gh = fake_gh({})
    assert main([]) == 0
    assert gh.calls == []


def test_main_fails_when_gh_fails(fake_gh, capsys) -> None:
    """The first failure stops the run, as ``set -e`` did."""
    gh = fake_gh({7: pull(), 8: pull()}, fail=("pr", "merge"))
    assert main(["7", "8"]) == 1
    assert gh.calls[-1][-1] == "7"
    out = capsys.readouterr().out
    assert "::error::gh pr merge --auto --merge --match-head-commit abc123 7 failed: GraphQL: nope" in out
