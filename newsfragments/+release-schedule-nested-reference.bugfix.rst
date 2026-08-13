Fix ``shared-release-schedule`` failing for every caller outside this repository.
It reached ``shared-release`` through the ``./.github/workflows`` shorthand, which GitHub resolves against the calling repository - none of which hold a ``shared-release.yml``. Only this repository's own caller exercised that path, where the shorthand does resolve, which kept the breakage hidden.
