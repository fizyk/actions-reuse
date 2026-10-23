"""Real commit messages, copied from the pull requests named above each."""

# fizyk/pyramid_fullauth#999: a security update, so no update-type.
URLLIB3_HEADLINE = "Bump urllib3 from 2.7.0 to 2.8.0"
URLLIB3_BODY = """\
Bumps [urllib3](https://github.com/urllib3/urllib3) from 2.7.0 to 2.8.0.
- [Release notes](https://github.com/urllib3/urllib3/releases)
- [Changelog](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst)
- [Commits](https://github.com/urllib3/urllib3/compare/2.7.0...2.8.0)

---
updated-dependencies:
- dependency-name: urllib3
  dependency-version: 2.8.0
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/pyramid_fullauth#1000: a security update fixing an advisory with a major bump.
OAUTHLIB_HEADLINE = "Bump oauthlib from 3.3.1 to 4.0.0"
OAUTHLIB_BODY = """\
Bumps [oauthlib](https://github.com/oauthlib/oauthlib) from 3.3.1 to 4.0.0.
- [Release notes](https://github.com/oauthlib/oauthlib/releases)
- [Changelog](https://github.com/oauthlib/oauthlib/blob/master/CHANGELOG.rst)
- [Commits](https://github.com/oauthlib/oauthlib/compare/v3.3.1...v4.0.0)

---
updated-dependencies:
- dependency-name: oauthlib
  dependency-version: 4.0.0
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/actions-reuse#370: a pre-commit hook, named by URL, so the headline is cut short.
ZIZMOR_HEADLINE = "Bump https://github.com/zizmorcore/zizmor-pre-commit"
ZIZMOR_BODY = """\
Bumps [https://github.com/zizmorcore/zizmor-pre-commit](https://github.com/zizmorcore/zizmor-pre-commit) \
from v1.30.0 to 1.30.1.
- [Release notes](https://github.com/zizmorcore/zizmor-pre-commit/releases)
- [Commits](https://github.com/zizmorcore/zizmor-pre-commit/compare/v1.30.0...v1.30.1)

---
updated-dependencies:
- dependency-name: https://github.com/zizmorcore/zizmor-pre-commit
  dependency-version: 1.30.1
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] <support@github.com>"""

# fizyk/actions-reuse#392: one grouped action bump across four directories.
SETUP_UV_HEADLINE = "Bump the setup-uv group across 4 directories with 1 update"
SETUP_UV_BODY = (
    "Bumps the setup-uv group with 1 update in the / directory: "
    "[astral-sh/setup-uv](https://github.com/astral-sh/setup-uv).\n"
    "\n"
    "Updates `astral-sh/setup-uv` from 10.2.0 to 10.3.0\n"
    "\n"
    "---\n"
    "updated-dependencies:\n"
    + "".join(
        "- dependency-name: astral-sh/setup-uv\n"
        "  dependency-version: 10.3.0\n"
        "  dependency-type: direct:production\n"
        "  update-type: version-update:semver-minor\n"
        "  dependency-group: setup-uv\n"
        for _ in range(4)
    )
    + "...\n\nSigned-off-by: dependabot[bot] <support@github.com>"
)

# fizyk/port-for#496: a requirement range widened, so no update-type and no versions.
UV_BUILD_HEADLINE = "Update uv-build requirement from <0.13,>=0.12 to >=0.12,<0.14"
UV_BUILD_BODY = """\
Updates the requirements on [uv-build](https://github.com/astral-sh/uv) to permit the latest version.
- [Release notes](https://github.com/astral-sh/uv/releases)
- [Changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/uv/compare/0.12.0...0.13.0)

---
updated-dependencies:
- dependency-name: uv-build
  dependency-version: 0.13.0
  dependency-type: direct:development
...

Signed-off-by: dependabot[bot] <support@github.com>"""
