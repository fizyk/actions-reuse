``shared-automerge`` now requires ``allow_auto_merge`` to be enabled on the calling repository.
Callers that take this version without enabling it fail with "Auto-merge is not allowed for this repository".
Enable it with ``gh api -X PATCH repos/OWNER/REPO -F allow_auto_merge=true``.
