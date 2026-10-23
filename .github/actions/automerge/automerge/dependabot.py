"""Dependabot: the equivalent of merge-me-action's DEPENDABOT_MINOR preset.

Read from the metadata dependabot writes into the commit message rather than parsed out
of the pull request title. Only update types known not to be majors are armed.
"""

import logging
import re

from automerge.decision import Decision

logger = logging.getLogger(__name__)

ALLOWED_TYPES = frozenset({"version-update:semver-minor", "version-update:semver-patch"})

VERSION = r"v?([0-9]+(?:\.[0-9]+)*)"
# `Bump <name> from <old> to <new>[ in <directory>]`
HEADLINE_RE = re.compile(rf"Bump .+ from {VERSION} to {VERSION}(?: in .+)?")
# `Bumps [<name>](<url>) from <old> to <new>.`
BUMPS_RE = re.compile(rf"Bumps \[[^]]+\]\([^)]+\) from {VERSION} to {VERSION}\.")
DEPENDENCY_RE = re.compile(r"^- dependency-name:", re.MULTILINE)
UPDATE_TYPE_RE = re.compile(r"version-update:[a-z-]*")
# `Update <name> requirement from <old range> to <new range>[ in <directory>]`
REQUIREMENT_RE = re.compile(r"Update .+ requirement from (.+) to (.+?)(?: in /.*)?")
# One constraint of a Python range (`>=1.2`, `~=1.2`, `!=2.*`, a bare version), its
# pre-release or build suffix included so the suffix's numbers are not read as versions.
CONSTRAINT = (
    r"(<=|>=|==|~=|!=|<|>)?\s*v?([0-9]+(?:\.[0-9]+)*)(\.\*)?"
    r"(?:[-+][0-9A-Za-z.+-]*|\.?[A-Za-z][0-9A-Za-z.+-]*)?"
)
CONSTRAINT_RE = re.compile(CONSTRAINT)
# Constraints joined by commas, and nothing else.
RANGE_RE = re.compile(rf"\s*{CONSTRAINT}(?:\s*,\s*{CONSTRAINT})*\s*")


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

    version_ranges = read_version_ranges(headline)
    if version_ranges is not None:
        logger.debug("No update-type, judging %r as a requirement range update.", headline)
        if dependencies != 1:
            return Decision(False, "does not update exactly one requirement, skipping.")
        old_version_range, new_version_range = version_ranges
        old_major_version = extract_latest_major_from_range(old_version_range)
        new_major_version = extract_latest_major_from_range(new_version_range)
        logger.debug("Newest major allowed: %s before, %s after.", old_major_version, new_major_version)
        if old_major_version is None or new_major_version is None:
            unreadable = old_version_range if old_major_version is None else new_version_range
            return Decision(False, f"has a range {unreadable} that does not read cleanly, skipping.")
        if new_major_version != old_major_version:
            return Decision(False, f"widens {old_version_range} to {new_version_range}, a new major version, skipping.")
        return Decision(True, f"widens {old_version_range} to {new_version_range}, not a new major version.")

    # Dependabot leaves `update-type` out of security updates and pre-commit updates,
    # so fall back to the versions in the commit headline. A long dependency name
    # (pre-commit names hooks by their repository URL) gets the headline cut down to
    # `Bump <name>`, so then read the versions from the body's `Bumps` line instead.
    # Anything that does not read cleanly as a single dependency moving between plain
    # dotted versions is skipped, so a major bump fixing an advisory cannot slip through.
    versions = read_versions(headline, body) if dependencies == 1 else None
    if versions is None:
        return Decision(False, "has no update type and no versions to compare, skipping.")
    old_version, new_version = versions
    if is_major_bump(old_version, new_version):
        return Decision(False, f"bumps {old_version} to {new_version}, a major version bump, skipping.")
    return Decision(True, f"bumps {old_version} to {new_version}, not a major version bump.")


def read_version_ranges(headline: str) -> tuple[str, str] | None:
    """The old and new ranges of a requirement update, without any directory suffix."""
    match = REQUIREMENT_RE.fullmatch(headline)
    if match is None:
        return None
    return match.group(1), match.group(2)


def extract_latest_major_from_range(version_range: str) -> int | None:
    """The newest major version *version_range* allows, or ``None`` if it allows none.

    Any syntax beyond Python's, such as ``^1.2`` or ``||``, gives ``None`` too, rather
    than a guess. ``>`` and ``>=`` raise the floor; other operators cap the major, ``<2``
    below 2. Only ``!=2.*`` rules a whole major out. With no cap, the floor stands in, so a
    raised minimum (``>=7`` to ``>=8``) reads as a new major.
    """
    if not RANGE_RE.fullmatch(version_range):
        logger.debug("Range %r is not comma-joined Python constraints.", version_range)
        return None
    floors = []
    caps = []
    excluded = set()
    for operator, version, wildcard in CONSTRAINT_RE.findall(version_range):
        major, *rest = (int(part) for part in version.split("."))
        if operator == "!=":
            if wildcard and not rest:
                excluded.add(major)
        elif operator in {">", ">="}:
            floors.append(major)
        else:
            caps.append(major - 1 if operator == "<" and not any(rest) else major)
    logger.debug("Range %r: floors %s, caps %s, excluded majors %s.", version_range, floors, caps, excluded)
    floor = max(floors, default=0)
    newest = min(caps, default=floor)
    while newest in excluded:
        newest -= 1
    return newest if newest >= floor else None


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
