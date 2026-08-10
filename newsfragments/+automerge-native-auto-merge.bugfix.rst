Arm GitHub's native auto-merge in ``shared-automerge`` instead of merging immediately.
The previous approach still lost a race against external checks reporting through the Statuses API, such as pre-commit.ci: those land after the last ``workflow_run``/``check_suite`` event fires, so the merge was rejected for a pending required check and nothing re-triggered the workflow.
Callers must enable ``allow_auto_merge`` on the repository.
