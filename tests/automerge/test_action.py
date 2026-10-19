"""Tests for ``action.yml``: the wiring between the workflow, the action and this suite."""

import json

from pathlib import Path

import yaml

import automerge


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / ".github" / "actions" / "automerge" / "action.yml"
WORKFLOW = ROOT / ".github" / "workflows" / "shared-automerge.yml"


def test_the_package_ships_next_to_the_action() -> None:
    """``$GITHUB_ACTION_PATH`` on the path is what makes the package importable at all."""
    assert Path(automerge.__file__).resolve().parent.parent == ACTION.parent
    (step,) = [step for step in yaml.safe_load(ACTION.read_text())["runs"]["steps"] if "run" in step]
    assert 'PYTHONPATH="$GITHUB_ACTION_PATH"' in step["run"]
    assert 'python -m automerge -- "$PULL_REQUESTS"' in step["run"]
    assert step["env"]["PULL_REQUESTS"] == "${{ inputs.pull-requests }}"


def test_the_workflow_calls_the_action() -> None:
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["merge-me"]["steps"]
    (step,) = [step for step in steps if "automerge" in step.get("uses", "")]
    assert step["uses"] == "$/.github/actions/automerge"
    assert set(step["with"]) == {"github-token", "pull-requests"}


def test_the_suite_runs_on_the_python_the_action_uses() -> None:
    action = yaml.safe_load(ACTION.read_text())
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "tests.yml").read_text())
    tested = json.loads(workflow["jobs"]["pytest"]["with"]["python-versions"])
    assert tested == [action["inputs"]["python-version"]["default"]]
