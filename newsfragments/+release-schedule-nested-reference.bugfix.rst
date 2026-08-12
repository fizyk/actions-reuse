Fix ``shared-release-schedule`` failing for every caller outside this repository.
It reached ``shared-release`` through the ``./.github/workflows`` shorthand, which GitHub resolves against the calling repository - none of which hold a ``shared-release.yml`` - so the nested call could not be resolved.
Only this repository's own caller exercised that path, and there the shorthand resolves because caller and callee do share a repository, which kept the breakage hidden.
The reference is now explicit and version-pinned like the other self-references.
