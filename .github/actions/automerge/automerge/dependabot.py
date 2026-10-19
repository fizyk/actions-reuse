"""Dependabot: the equivalent of merge-me-action's DEPENDABOT_MINOR preset.

Read from the metadata dependabot writes into the commit message rather than parsed out
of the pull request title. Only update types known not to be majors are armed.
"""

import re

from automerge.decision import Decision

ALLOWED_TYPES = frozenset({"version-update:semver-minor", "version-update:semver-patch"})

VERSION = r"v?([0-9]+(?:\.[0-9]+)*)"
# `Bump <name> from <old> to <new>[ in <directory>]`
HEADLINE_RE = re.compile(rf"Bump .+ from {VERSION} to {VERSION}(?: in .+)?")
# `Bumps [<name>](<url>) from <old> to <new>.`
BUMPS_RE = re.compile(rf"Bumps \[[^]]+\]\([^)]+\) from {VERSION} to {VERSION}\.")
DEPENDENCY_RE = re.compile(r"^- dependency-name:", re.MULTILINE)
UPDATE_TYPE_RE = re.compile(r"version-update:[a-z-]*")


def decide(headline: str, body: str) -> Decision:
    """Judge a dependabot pull request by the message of its latest commit."""
    dependencies = len(DEPENDENCY_RE.findall(body))
    if "version-update:" in body:
        # A grouped update lists one entry per dependency, so every entry has to be a
        # minor or patch: one major among them, or an entry without an update type,
        # skips the whole pull request.
        update_types = UPDATE_TYPE_RE.findall(body)
        if not ALLOWED_TYPES.issuperset(update_types) or len(update_types) != dependencies:
            return Decision(False, "is not solely minor or patch version bumps, skipping.")
        return Decision(True, "is solely minor or patch version bumps.")

    # Dependabot leaves `update-type` out of security updates and pre-commit updates,
    # so fall back to the versions in the commit headline. A long dependency name
    # (pre-commit names hooks by their repository URL) gets the headline cut down to
    # `Bump <name>`, so then read the versions from the body's `Bumps` line instead.
    # Anything that does not read cleanly as a single dependency moving between plain
    # dotted versions is skipped, so a major bump fixing an advisory cannot slip through.
    versions = read_versions(headline, body) if dependencies == 1 else None
    if versions is None:
        return Decision(False, "has no update type and no versions to compare, skipping.")
    old, new = versions
    if is_major_bump(old, new):
        return Decision(False, f"bumps {old} to {new}, a major version bump, skipping.")
    return Decision(True, f"bumps {old} to {new}, not a major version bump.")


def read_versions(headline: str, body: str) -> tuple[str, str] | None:
    """The old and new versions of a single-dependency bump, without any ``v`` prefix."""
    match = HEADLINE_RE.fullmatch(headline)
    if match is None:
        bumps = next((line for line in body.splitlines() if line.startswith("Bumps ")), "")
        match = BUMPS_RE.fullmatch(bumps)
    if match is None:
        return None
    return match.group(1), match.group(2)


def is_major_bump(old: str, new: str) -> bool:
    """Whether the major version moves - or, before 1.0, the minor version, the breaking one there."""
    old_major, old_minor = _major_minor(old)
    new_major, new_minor = _major_minor(new)
    return old_major != new_major or (old_major == 0 and old_minor != new_minor)


def _major_minor(version: str) -> tuple[int, int]:
    parts = [int(part) for part in version.split(".")]
    return parts[0], parts[1] if len(parts) > 1 else 0
