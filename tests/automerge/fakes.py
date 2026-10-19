"""A stand-in for ``gh``, installed in place of ``subprocess.run``."""

import json
import subprocess


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
