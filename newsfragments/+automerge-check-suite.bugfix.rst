Trigger automerge on ``check_suite`` completion in addition to ``workflow_run``, so the merge is no longer raced by external checks such as pre-commit.ci that finish after the in-repo workflows
