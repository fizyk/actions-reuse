"""Plan the next release: whether one is warranted, and which version it carries.

A release is planned when there are commits since the latest ``[v]MAJOR.MINOR.PATCH``
tag. The level follows the newsfragments present: major for a type listed in
``major-fragments``, minor for one in ``minor-fragments``, patch otherwise.

towncrier decides what counts as a newsfragment. The fragment directory and the types
come from the repository's own towncrier configuration, and every filename goes through
towncrier's parser, so custom types, sections, the counter form and extension-less
fragments all count, and anything towncrier does not recognise is reported.

``towncrier._builder`` and ``towncrier._settings.load`` are private API, so the action
installs the towncrier version this repository pins and tests against: a break in that
surface fails a check here rather than a consumer's release.
"""

import dataclasses
import os
import re
import subprocess
import sys

from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path

from towncrier._builder import FragmentsPath, parse_newfragment_basename
from towncrier._settings.load import ConfigError, load_config

LEVELS = ("major", "minor", "patch")

# A README living among the fragments is a README, not a fragment nobody can parse.
IGNORED_FILES = ("readme", "readme.md", "readme.rst")

# Prerelease and build metadata (v1.2.3-rc1, v1.2.3+build) bump from the release core.
# Zero-padded components are refused: 1.010.0 is not a semver version, so guessing at
# which of 1.10.0 or 1.1.0 was meant is worse than reporting the problem.
TAG_RE = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:[-+].*)?")


class PlanError(Exception):
    """The repository cannot release as configured."""


@dataclasses.dataclass(frozen=True)
class Fragments:
    """The fragments directory as towncrier reads it.

    ``unparsed`` holds files that towncrier does not recognise as newsfragments. An
    empty fragments directory is the normal state of a quiet repository, but files
    that no fragment type claims mean a repository that would never release.
    """

    categories: frozenset[str] = frozenset()
    unparsed: tuple[str, ...] = ()
    directories: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    configured: bool = True


@dataclasses.dataclass(frozen=True)
class Plan:
    """The release decision, ready to be turned into step outputs."""

    should_release: bool
    version: str | None = None
    level: str | None = None
    reason: str = ""
    warning: str | None = None


def split_types(spec: str) -> frozenset[str]:
    """Read a comma-separated list of towncrier types out of a workflow input."""
    return frozenset(part.strip() for part in spec.split(",") if part.strip())


def collect_fragments(base_dir: str | os.PathLike[str] = ".") -> Fragments:
    """Classify every file in the repository's towncrier fragment directories."""
    try:
        config = load_config(os.fspath(base_dir))
    except ConfigError as error:
        raise PlanError(f"Cannot read the towncrier configuration: {error}") from error
    if config is None:
        return Fragments(configured=False)

    ignored = set(IGNORED_FILES)
    if isinstance(config.template, str):
        # A template kept inside the fragments directory is not a fragment. Its other
        # form, a (package, resource) pair, does not live there at all.
        ignored.add(os.path.basename(config.template).lower())
    if config.ignore:
        ignored.update(name.lower() for name in config.ignore)

    fragments_path = FragmentsPath(os.fspath(base_dir), config)
    categories: set[str] = set()
    unparsed: list[str] = []
    directories: list[str] = []
    missing: list[str] = []

    for section_directory in config.sections.values():
        directory = Path(fragments_path(section_directory))
        if not directory.is_dir():
            missing.append(str(directory))
            continue
        directories.append(str(directory))
        for path in sorted(directory.iterdir()):
            # A directory named like a fragment is not one, and a hidden file is
            # never a deliberate fragment - .gitkeep is how an empty fragments
            # directory is kept in git in the first place.
            if not path.is_file() or path.name.startswith("."):
                continue
            if any(fnmatch(path.name.lower(), pattern) for pattern in ignored):
                continue
            _, category, _ = parse_newfragment_basename(path.name, config.types)
            if category is None:
                unparsed.append(str(path))
            else:
                categories.add(category)

    return Fragments(
        categories=frozenset(categories),
        unparsed=tuple(unparsed),
        directories=tuple(directories),
        missing=tuple(missing),
        configured=True,
    )


def bump_level(
    categories: Iterable[str],
    minor_types: Iterable[str],
    major_types: Iterable[str],
) -> str:
    """Pick the bump level for the fragment types present: major, then minor, then patch."""
    present = frozenset(categories)
    if present & frozenset(major_types):
        return "major"
    if present & frozenset(minor_types):
        return "minor"
    return "patch"


def parse_tag(tag: str) -> tuple[int, int, int]:
    """Read the release core out of a git tag."""
    match = TAG_RE.fullmatch(tag.strip())
    if match is None:
        raise PlanError(
            f"Cannot derive the next version from tag '{tag}': "
            "expected [v]MAJOR.MINOR.PATCH."
        )
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def bump(core: tuple[int, int, int], level: str) -> str:
    """Raise a version core by one level."""
    major, minor, patch = core
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    if level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown bump level '{level}'; expected one of {', '.join(LEVELS)}.")


def decide(
    *,
    tag: str | None,
    commit_count: int,
    fragments: Fragments,
    minor_types: Iterable[str] = (),
    major_types: Iterable[str] = (),
    required: bool = False,
) -> Plan:
    """Turn the gathered facts into a release decision.

    Pure: every fact it needs is an argument, so the whole decision is testable
    without a git repository, a checkout, or a workflow run.
    """
    if tag is None:
        return Plan(
            should_release=False,
            reason="Nothing to release.",
            warning="No tags found, so there is no version to bump from; skipping release.",
        )
    if commit_count == 0:
        return Plan(
            should_release=False,
            reason=f"No commits since {tag}; nothing to release.",
        )

    # Refuse an unparseable tag before any later check can turn the run into a quiet
    # skip: such a repository needs attention either way.
    core = parse_tag(tag)

    if required:
        if not fragments.configured:
            raise PlanError(
                "newsfragments-required is set but no towncrier configuration was found."
            )
        if not fragments.directories:
            listed = ", ".join(f"'{path}'" for path in fragments.missing)
            raise PlanError(
                f"newsfragments-required is set but no newsfragments directory "
                f"exists: {listed}."
            )
        if not fragments.categories:
            if fragments.unparsed:
                listed = ", ".join(fragments.unparsed)
                raise PlanError(
                    f"No newsfragments found, but the fragments directory holds "
                    f"{len(fragments.unparsed)} file(s) that towncrier does not "
                    f"recognise as newsfragments: {listed}. Check the file names "
                    f"against the towncrier types configured for this repository."
                )
            # An empty fragments directory is the normal state of a quiet repository
            # and must stay quiet.
            return Plan(
                should_release=False,
                reason=(
                    "newsfragments-required is set and no newsfragments were found; "
                    "skipping release."
                ),
            )

    level = bump_level(fragments.categories, minor_types, major_types)
    version = bump(core, level)
    return Plan(
        should_release=True,
        version=version,
        level=level,
        reason=f"Bumping {level}: {tag} -> {version}.",
    )


def git(*args: str, cwd: str | os.PathLike[str] = ".") -> str:
    """Run git and return its stdout, stripped. A failed command is a PlanError."""
    try:
        completed = subprocess.run(
            ("git", *args),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or f"exit status {error.returncode}"
        raise PlanError(f"git {' '.join(args)} failed: {detail}") from error
    return completed.stdout.strip()


def latest_tag(cwd: str | os.PathLike[str] = ".") -> str | None:
    """The most recent tag reachable from HEAD, or None when nothing is tagged."""
    # `git describe` fails the same way whether nothing is tagged or the checkout is
    # unusable, and only the first of those is a quiet skip. Listing reachable tags
    # tells them apart: it succeeds with no output when there is simply no tag, and
    # fails when there is no repository or no HEAD to reach one from.
    if not git("tag", "--merged", "HEAD", cwd=cwd):
        return None
    return git("describe", "--tags", "--abbrev=0", cwd=cwd) or None


def commits_since(tag: str, cwd: str | os.PathLike[str] = ".") -> int:
    """How many commits landed since *tag*."""
    return int(git("rev-list", f"{tag}..HEAD", "--count", cwd=cwd))


def write_outputs(**values: str) -> None:
    """Append step outputs to the file GitHub gave us, if we are running in Actions."""
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main(cwd: str | os.PathLike[str] = ".") -> int:
    required = os.environ.get("NEWSFRAGMENTS_REQUIRED", "").strip().lower() == "true"
    minor_types = split_types(os.environ.get("MINOR_FRAGMENTS", ""))
    major_types = split_types(os.environ.get("MAJOR_FRAGMENTS", ""))

    try:
        tag = latest_tag(cwd)
        commit_count = commits_since(tag, cwd) if tag is not None else 0
        print(f"Latest tag: {tag or '(none)'}")
        print(f"Commits since tag: {commit_count}")

        fragments = collect_fragments(cwd)
        if fragments.configured:
            found = ", ".join(sorted(fragments.categories)) or "(none)"
            print(f"Newsfragment types found: {found}")
            for path in fragments.unparsed:
                print(f"Not a newsfragment: {path}")
            for path in fragments.missing:
                print(f"No fragments directory at {path}.")
        else:
            print("No towncrier configuration found; continuing without newsfragments.")

        plan = decide(
            tag=tag,
            commit_count=commit_count,
            fragments=fragments,
            minor_types=minor_types,
            major_types=major_types,
            required=required,
        )
    except PlanError as error:
        print(f"::error::{error}")
        return 1

    if plan.warning:
        print(f"::warning::{plan.warning}")
    print(plan.reason)

    if plan.should_release:
        assert plan.version is not None
        write_outputs(should_release="true", version=plan.version)
    else:
        write_outputs(should_release="false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
