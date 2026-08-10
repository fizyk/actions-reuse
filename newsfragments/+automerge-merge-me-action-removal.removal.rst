Remove the ``ridedott/merge-me-action`` dependency from ``shared-automerge``.
The author and version-bump gates it provided are kept: only ``dependabot`` and ``pre-commit-ci`` pull requests are armed, and major version bumps are skipped, now determined from the update metadata dependabot writes into the commit message rather than parsed out of the pull request title.
``permission-administration: read`` is no longer requested for the app token.
