Drop the ``allow-prereleases`` input from the ``uv`` and ``uv-setup`` actions
(and from ``shared-tests-pytests``/``shared-pr-check``/``shared-release`` callsites):
uv has no CLI flag to forbid pre-release fallback, so the input was non-functional.
uv selects a pre-release only when no matching stable Python is available.
