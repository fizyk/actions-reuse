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
# `Update <name> requirement from <old range> to <new range>[ in <directory>]`
REQUIREMENT_RE = re.compile(r"Update .+ requirement from (.+) to .+")
DEPENDENCY_VERSION_RE = re.compile(r"^  dependency-version: (.*)$", re.MULTILINE)
PLAIN_VERSION_RE = re.compile(r"[0-9]+(?:\.[0-9]+)*")
# One constraint of a Python range: `>=1.2`, `<2`, `~=1.2`, `1.2.*`, `== 1.2.3`, or a bare
# version. A pre-release or build suffix (`-beta.2`, `b2`, `+build.7`) is consumed with its
# version, so its numbers are not read as constraints of their own. Other ecosystems'
# operators, such as `^` or `~>`, are left out until there is a range of theirs to read.
CONSTRAINT = (
    r"(<=|>=|==|~=|!=|<|>)?\s*v?([0-9]+(?:\.[0-9]+)*)(\.\*)?"
    r"(?:[-+][0-9A-Za-z.+-]*|\.?[A-Za-z][0-9A-Za-z.+-]*)?"
)
CONSTRAINT_RE = re.compile(CONSTRAINT)
# A whole range: constraints joined by commas, and nothing else.
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

    # Widening a requirement range is not a version update, so dependabot writes no
    # `update-type` for it either, and its headline carries ranges, not versions.
    # Judge it by the newest version it now permits, armed when the old range already
    # allowed that version's major.
    if REQUIREMENT_RE.fullmatch(headline) is not None:
        if dependencies != 1:
            return Decision(False, "does not update exactly one requirement, skipping.")
        requirement = read_requirement(headline, body)
        if requirement is None:
            return Decision(False, "has no plain dependency-version to compare, skipping.")
        old_range, new_version = requirement
        old_major = range_major(old_range)
        if old_major is None:
            return Decision(False, f"has a range {old_range} that does not read cleanly, skipping.")
        if range_major(new_version) != old_major:
            return Decision(False, f"widens {old_range} to permit {new_version}, a new major version, skipping.")
        return Decision(True, f"widens {old_range} to permit {new_version}, not a new major version.")

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


def read_requirement(headline: str, body: str) -> tuple[str, str] | None:
    """The old range of a requirement update and the newest version it now permits.

    The range comes from the headline, the version from the metadata's
    ``dependency-version``, which has to be a plain dotted version.
    """
    match = REQUIREMENT_RE.fullmatch(headline)
    versions = DEPENDENCY_VERSION_RE.findall(body)
    new = versions[0].strip() if versions else ""
    if match is None or not PLAIN_VERSION_RE.fullmatch(new):
        return None
    return match.group(1), new


def range_major(requirement: str) -> int | None:
    """The newest major version *requirement* allows, or ``None`` when it does not read cleanly.

    Any syntax not known to read correctly, such as another ecosystem's ``^1.2`` or
    alternatives joined by ``||``, gives ``None`` rather than a guess, so a misread range
    cannot arm a major. Every constraint has to hold at once: ``>`` and ``>=`` only
    raise the floor, every other operator caps the major at its own: ``~=1.2``,
    ``==1.2.3`` and ``1.2.*`` all stay within 1.
    An exclusive bound on a bare major, such as ``<2`` or ``<2.0.0``, stops below that
    major, so it allows the one before. ``!=`` excludes rather than allows: only a
    prefix exclusion of a whole major, such as ``!=2.*``, rules that major out, so the
    newest one steps down past it. A range that allows nothing gives ``None``.
    """
    if not RANGE_RE.fullmatch(requirement):
        return None
    floors = []
    caps = []
    excluded = set()
    for operator, version, wildcard in CONSTRAINT_RE.findall(requirement):
        major, *rest = (int(part) for part in version.split("."))
        if operator == "!=":
            if wildcard and not rest:
                excluded.add(major)
        elif operator in {">", ">="}:
            floors.append(major)
        else:
            caps.append(major - 1 if operator == "<" and not any(rest) else major)
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
