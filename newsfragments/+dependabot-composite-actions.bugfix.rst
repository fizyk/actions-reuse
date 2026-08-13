Bump ``astral-sh/setup-uv`` to 10.0.0, which no longer prunes the cache by default.
Dependabot had never updated it in ``uv-setup`` and ``uv-build``: ``directory: "/"`` reaches the workflows but not ``.github/actions``, so the pins there are now watched explicitly.
