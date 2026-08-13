"""Tests for the release planner behind the ``release-plan`` composite action."""

import json

from importlib.metadata import version
from pathlib import Path

import pytest
import yaml

import release_plan

from release_plan import (
    Fragments,
    Plan,
    PlanError,
    bump,
    bump_level,
    collect_fragments,
    commits_since,
    decide,
    latest_tag,
    main,
    parse_tag,
    split_types,
)

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parent.parent
ACTION = ROOT / ".github" / "actions" / "release-plan" / "action.yml"

CUSTOM_TYPES = """\
[tool.towncrier]
directory = "newsfragments"

[[tool.towncrier.type]]
directory = "break"
name = "Backward incompatible changes"
showcontent = true

[[tool.towncrier.type]]
directory = "depr"
name = "Deprecations"
showcontent = true

[[tool.towncrier.type]]
directory = "feature"
name = "Features"
showcontent = true
"""


# What towncrier calls a fragment, and what it does not: the naming rules the planner
# has to hold to, case by case.


@pytest.mark.parametrize(
    ("name", "category"),
    [
        ("790.feature.rst", "feature"),
        # towncrier's counter form, appended for a second fragment of one type on one
        # issue.
        ("790.feature.1.rst", "feature"),
        # The parser scans dot-parts from the back, so the last valid type wins.
        ("790.feature.1.misc.rst", "misc"),
        ("790.feature.extra.rst", "feature"),
        # Extension-less fragments are valid towncrier.
        ("790.feature", "feature"),
        ("790.misc.rst", "misc"),
        ("790.bugfix.rst", "bugfix"),
        ("790.removal.rst", "removal"),
        # The extension is never consulted, so markdown needs no configuring.
        ("790.feature.md", "feature"),
        # Orphan fragments carry the orphan prefix instead of an issue number.
        ("+something-cool.feature.rst", "feature"),
        # Nor does an issue number have to be a number.
        ("fix-1.2.3.feature", "feature"),
    ],
)
def test_fragment_is_recognised(make_repo, name: str, category: str) -> None:
    fragments = collect_fragments(make_repo(name))
    assert fragments.categories == frozenset({category})
    assert fragments.unparsed == ()


@pytest.mark.parametrize(
    "name",
    [
        "README.rst",
        "readme.md",
        ".gitignore",
        ".gitkeep",
        ".keep",
        # A directory matching the fragment shape is not a fragment.
        "790.feature.rst/",
    ],
)
def test_fragment_is_ignored(make_repo, name: str) -> None:
    fragments = collect_fragments(make_repo(name))
    assert fragments.categories == frozenset()
    assert fragments.unparsed == ()


@pytest.mark.parametrize(
    "name",
    [
        # A typo in the type: no type claims it, so it would never be released.
        "790.feat.rst",
        "790.rst",
        # A single part cannot carry a type.
        "feature",
    ],
)
def test_fragment_is_unrecognised(make_repo, name: str) -> None:
    fragments = collect_fragments(make_repo(name))
    assert fragments.categories == frozenset()
    assert [Path(path).name for path in fragments.unparsed] == [name]


def test_custom_types(make_repo) -> None:
    """Custom types come from the repository's configuration, not from a guess."""
    repo = make_repo("790.break.rst", "791.depr.rst", config=CUSTOM_TYPES)
    assert collect_fragments(repo).categories == frozenset({"break", "depr"})


def test_custom_types_replace_the_defaults(make_repo) -> None:
    """A default type is not a type once the repository declares its own."""
    fragments = collect_fragments(make_repo("790.bugfix.rst", config=CUSTOM_TYPES))
    assert fragments.categories == frozenset()
    assert [Path(path).name for path in fragments.unparsed] == ["790.bugfix.rst"]


def test_configured_directory(make_repo) -> None:
    """The fragments directory comes from towncrier's own ``directory`` setting."""
    repo = make_repo(
        "790.feature.rst",
        config='[tool.towncrier]\ndirectory = "changes/news"\n',
        directory="changes/news",
    )
    fragments = collect_fragments(repo)
    assert fragments.categories == frozenset({"feature"})
    assert fragments.directories == (str(repo / "changes" / "news"),)


def test_package_relative_default_directory(tmp_path: Path) -> None:
    """Without ``directory``, towncrier looks under the package."""
    (tmp_path / "towncrier.toml").write_text('[tool.towncrier]\npackage = "thing"\n')
    news = tmp_path / "thing" / "newsfragments"
    news.mkdir(parents=True)
    (news / "790.feature.rst").write_text("A thing.\n")
    assert collect_fragments(tmp_path).categories == frozenset({"feature"})


def test_sections(make_repo) -> None:
    """Fragments are collected from every configured section."""
    config = """\
    [tool.towncrier]
    directory = "newsfragments"

    [[tool.towncrier.section]]
    path = ""

    [[tool.towncrier.section]]
    name = "Web"
    path = "web"
    """
    repo = make_repo("790.bugfix.rst", "web/791.feature.rst", config=config)
    fragments = collect_fragments(repo)
    assert fragments.categories == frozenset({"bugfix", "feature"})
    assert fragments.missing == ()


def test_ignore_setting(make_repo) -> None:
    """towncrier's own ``ignore`` list is honoured."""
    config = """\
    [tool.towncrier]
    directory = "newsfragments"
    ignore = ["TODO.rst"]
    """
    fragments = collect_fragments(make_repo("TODO.rst", config=config))
    assert fragments.unparsed == ()


def test_template_in_the_fragments_directory(make_repo) -> None:
    """A template kept among the fragments is not a fragment."""
    config = """\
    [tool.towncrier]
    directory = "newsfragments"
    template = "newsfragments/template.rst"
    """
    fragments = collect_fragments(make_repo("template.rst", config=config))
    assert fragments.unparsed == ()


def test_empty_directory(make_repo) -> None:
    fragments = collect_fragments(make_repo())
    assert fragments.configured
    assert fragments.categories == frozenset()
    assert fragments.unparsed == ()
    assert fragments.missing == ()


def test_missing_directory(make_repo) -> None:
    repo = make_repo(directory="")
    fragments = collect_fragments(repo)
    assert fragments.directories == ()
    assert fragments.missing == (str(repo / "newsfragments"),)


def test_no_towncrier_configuration(tmp_path: Path) -> None:
    assert collect_fragments(tmp_path) == Fragments(configured=False)


def test_broken_towncrier_configuration(make_repo) -> None:
    repo = make_repo(config='[tool.towncrier]\ntemplate = "nope.rst"\n')
    with pytest.raises(PlanError, match="Cannot read the towncrier configuration"):
        collect_fragments(repo)


# The bump level, and the inputs that decide it.


@pytest.mark.parametrize(
    ("categories", "minor", "major", "expected"),
    [
        ({"feature"}, {"feature"}, set(), "minor"),
        ({"bugfix"}, {"feature"}, set(), "patch"),
        ({"misc"}, {"feature", "break"}, set(), "patch"),
        # Pre-1.0: the breaking type sits in the minor list, so it never reaches 1.0.0.
        ({"break"}, {"feature", "break"}, set(), "minor"),
        ({"break"}, {"feature"}, {"break"}, "major"),
        # Major wins over a minor present in the same batch.
        ({"break", "feature"}, {"feature"}, {"break"}, "major"),
        (set(), {"feature"}, {"break"}, "patch"),
        # No policy configured at all: everything is a patch.
        ({"feature"}, set(), set(), "patch"),
    ],
)
def test_bump_level(categories, minor, major, expected: str) -> None:
    assert bump_level(categories, minor, major) == expected


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("feature", {"feature"}),
        ("feature,break", {"feature", "break"}),
        (" feature , break ", {"feature", "break"}),
        ("feature,,break,", {"feature", "break"}),
        ("", set()),
        ("   ", set()),
    ],
)
def test_split_types(spec: str, expected: set[str]) -> None:
    assert split_types(spec) == frozenset(expected)


# Reading a version out of a tag, and raising it.


@pytest.mark.parametrize(
    ("tag", "core"),
    [
        ("v1.2.3", (1, 2, 3)),
        ("1.2.3", (1, 2, 3)),
        ("v0.7.0", (0, 7, 0)),
        # Prerelease and build metadata bump from the release core.
        ("v1.5.0-rc1", (1, 5, 0)),
        ("v1.2.3+build.5", (1, 2, 3)),
        ("v1.2.3+build-5", (1, 2, 3)),
        ("v10.20.30", (10, 20, 30)),
    ],
)
def test_parse_tag(tag: str, core: tuple[int, int, int]) -> None:
    assert parse_tag(tag) == core


@pytest.mark.parametrize(
    "tag",
    [
        "nightly-2026",
        # Zero-padded components are not semver, and guessing is worse than failing.
        "1.010.0",
        "v1.2",
        "v1.2.3.4",
        "release",
        "",
    ],
)
def test_unparseable_tag(tag: str) -> None:
    with pytest.raises(PlanError, match=r"expected \[v\]MAJOR\.MINOR\.PATCH"):
        parse_tag(tag)


@pytest.mark.parametrize(
    ("level", "expected"),
    [("major", "2.0.0"), ("minor", "1.3.0"), ("patch", "1.2.4")],
)
def test_bump(level: str, expected: str) -> None:
    assert bump((1, 2, 3), level) == expected


def test_bump_from_zero_major() -> None:
    assert bump((0, 7, 0), "minor") == "0.8.0"


def test_bump_unknown_level() -> None:
    with pytest.raises(ValueError, match="Unknown bump level"):
        bump((1, 2, 3), "epoch")


# The decision itself, over facts rather than a repository.


def test_decide_without_tags() -> None:
    plan = decide(tag=None, commit_count=3, fragments=Fragments())
    assert plan == Plan(
        should_release=False,
        reason="Nothing to release.",
        warning="No tags found, so there is no version to bump from; skipping release.",
    )


def test_decide_without_commits_since_tag() -> None:
    plan = decide(tag="v1.2.3", commit_count=0, fragments=Fragments())
    assert not plan.should_release
    assert plan.reason == "No commits since v1.2.3; nothing to release."


def test_decide_rejects_an_unparseable_tag_before_any_quiet_skip() -> None:
    """A repository that cannot be released needs attention, not a green skip."""
    with pytest.raises(PlanError, match="Cannot derive the next version"):
        decide(
            tag="nightly-2026",
            commit_count=1,
            fragments=Fragments(),
            required=True,
        )


def test_decide_patch_without_fragments() -> None:
    plan = decide(
        tag="v1.2.3",
        commit_count=1,
        fragments=Fragments(),
        minor_types={"feature"},
    )
    assert plan.should_release
    assert plan.version == "1.2.4"
    assert plan.level == "patch"
    assert plan.reason == "Bumping patch: v1.2.3 -> 1.2.4."


def test_decide_minor_with_a_feature() -> None:
    plan = decide(
        tag="v1.2.3",
        commit_count=1,
        fragments=Fragments(categories=frozenset({"feature"})),
        minor_types={"feature"},
    )
    assert (plan.version, plan.level) == ("1.3.0", "minor")


def test_decide_major_with_a_break() -> None:
    plan = decide(
        tag="v2.9.4",
        commit_count=1,
        fragments=Fragments(categories=frozenset({"break"})),
        minor_types={"feature"},
        major_types={"break"},
    )
    assert (plan.version, plan.level) == ("3.0.0", "major")


def test_decide_break_on_a_pre_1_0_project() -> None:
    plan = decide(
        tag="v0.7.0",
        commit_count=1,
        fragments=Fragments(categories=frozenset({"break"})),
        minor_types={"feature", "break"},
    )
    assert (plan.version, plan.level) == ("0.8.0", "minor")


def test_decide_required_and_empty_skips_quietly() -> None:
    """A quiet repository must not report a failure every run."""
    plan = decide(
        tag="v1.2.3",
        commit_count=1,
        fragments=Fragments(directories=("newsfragments",)),
        required=True,
    )
    assert not plan.should_release
    assert plan.version is None
    assert plan.warning is None


def test_decide_required_and_missing_directory_fails() -> None:
    with pytest.raises(PlanError, match="no newsfragments directory exists"):
        decide(
            tag="v1.2.3",
            commit_count=1,
            fragments=Fragments(missing=("newsfragments",)),
            required=True,
        )


def test_decide_required_without_towncrier_configuration_fails() -> None:
    with pytest.raises(PlanError, match="no towncrier configuration"):
        decide(
            tag="v1.2.3",
            commit_count=1,
            fragments=Fragments(configured=False),
            required=True,
        )


def test_decide_required_with_only_unrecognised_files_fails() -> None:
    """Files nothing claims mean a repository that would never release."""
    with pytest.raises(PlanError, match=r"790\.feat\.rst"):
        decide(
            tag="v1.2.3",
            commit_count=1,
            fragments=Fragments(
                unparsed=("newsfragments/790.feat.rst",),
                directories=("newsfragments",),
            ),
            required=True,
        )


def test_decide_tolerates_unrecognised_files_when_not_required() -> None:
    plan = decide(
        tag="v1.2.3",
        commit_count=1,
        fragments=Fragments(
            unparsed=("newsfragments/790.feat.rst",),
            directories=("newsfragments",),
        ),
    )
    assert (plan.should_release, plan.version) == (True, "1.2.4")


def test_decide_tolerates_a_missing_directory_when_not_required() -> None:
    plan = decide(
        tag="v1.2.3",
        commit_count=1,
        fragments=Fragments(missing=("newsfragments",)),
    )
    assert (plan.should_release, plan.version) == (True, "1.2.4")


# End to end, over a real git repository and a real GITHUB_OUTPUT file.


def test_main_minor_release(make_repo, git_history, outputs, monkeypatch) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo, tag="v1.2.3", commits_after=1)
    monkeypatch.setenv("MINOR_FRAGMENTS", "feature")

    assert main(repo) == 0
    assert outputs() == {"should_release": "true", "version": "1.3.0"}


def test_main_without_commits_since_tag(make_repo, git_history, outputs) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo, tag="v1.2.3")

    assert main(repo) == 0
    assert outputs() == {"should_release": "false"}


def test_main_in_an_untagged_repository(
    make_repo, git_history, outputs, capsys
) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo)

    assert main(repo) == 0
    assert outputs() == {"should_release": "false"}
    assert "::warning::No tags found" in capsys.readouterr().out


def test_main_reports_misconfiguration_as_an_error(
    make_repo, git_history, outputs, monkeypatch, capsys
) -> None:
    repo = make_repo("790.feat.rst")
    git_history(repo, tag="v1.2.3", commits_after=1)
    monkeypatch.setenv("NEWSFRAGMENTS_REQUIRED", "true")

    assert main(repo) == 1
    assert outputs() == {}
    assert "::error::" in capsys.readouterr().out


def test_main_without_a_fragments_directory(
    make_repo, git_history, outputs, capsys
) -> None:
    repo = make_repo(directory="")
    git_history(repo, tag="v1.2.3", commits_after=1)

    assert main(repo) == 0
    assert outputs() == {"should_release": "true", "version": "1.2.4"}
    assert "No fragments directory at" in capsys.readouterr().out


def test_main_without_a_repository(make_repo, outputs, capsys) -> None:
    """An unusable checkout must not read as a repository with nothing to release."""
    assert main(make_repo("790.feature.rst")) == 1
    assert outputs() == {}
    assert "::error::git tag --merged HEAD failed" in capsys.readouterr().out


def test_latest_tag_reports_a_broken_checkout(tmp_path: Path) -> None:
    with pytest.raises(PlanError, match="not a git repository"):
        latest_tag(tmp_path)


def test_latest_tag_is_none_when_nothing_is_tagged(make_repo, git_history) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo)
    assert latest_tag(repo) is None


def test_commits_since_reports_an_unknown_revision(make_repo, git_history) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo, tag="v1.2.3")
    with pytest.raises(PlanError, match="git rev-list"):
        commits_since("v9.9.9", repo)


def test_main_without_towncrier_configuration(
    tmp_path: Path, git_history, outputs, capsys
) -> None:
    git_history(tmp_path, tag="v1.2.3", commits_after=1)

    assert main(tmp_path) == 0
    assert outputs() == {"should_release": "true", "version": "1.2.4"}
    assert "No towncrier configuration found" in capsys.readouterr().out


def test_main_outside_actions(make_repo, git_history, monkeypatch, capsys) -> None:
    repo = make_repo("790.feature.rst")
    git_history(repo, tag="v1.2.3", commits_after=1)
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)

    assert main(repo) == 0
    assert "Bumping patch: v1.2.3 -> 1.2.4." in capsys.readouterr().out


# One pin, and the suite runs against it - the planner reads towncrier's private API.


def test_the_action_installs_the_pin_from_this_project() -> None:
    """A second pin inside the action could drift from the one the suite exercises."""
    plan = _plan_step()
    assert "--only-group release-plan" in plan["run"]
    assert "towncrier==" not in plan["run"]
    assert "towncrier-version" not in yaml.safe_load(ACTION.read_text())["inputs"]


def test_the_pinned_group_holds_towncrier_alone() -> None:
    """The action installs the whole group into its own checkout, so it stays that small."""
    group = _groups()["release-plan"]
    assert len(group) == 1
    assert group[0].startswith("towncrier==")


def test_the_dev_group_includes_the_pinned_group() -> None:
    """tbump builds the changelog with ``uv run towncrier``, so it is needed by default too."""
    assert {"include-group": "release-plan"} in _groups()["dev"]


def test_the_installed_towncrier_is_the_pinned_one() -> None:
    """Otherwise a local environment can pass a suite that CI would fail."""
    assert version("towncrier") == _pinned()


def test_the_planner_ships_next_to_the_action() -> None:
    """``$GITHUB_ACTION_PATH`` is what makes the module reachable at all."""
    assert Path(release_plan.__file__).resolve().parent == ACTION.parent


def test_the_project_is_three_levels_above_the_action() -> None:
    """Which is the relative path the action walks up to find this pin."""
    assert ACTION.parent.parents[2] == ROOT
    assert '--project "$GITHUB_ACTION_PATH/../../.."' in _plan_step()["run"]


def test_the_suite_runs_on_the_python_the_action_uses() -> None:
    """The suite tests one interpreter, so it has to be the one the action ships."""
    action = yaml.safe_load(ACTION.read_text())
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "tests.yml").read_text())
    tested = json.loads(workflow["jobs"]["pytest"]["with"]["python-versions"])
    assert tested == [action["inputs"]["python-version"]["default"]]


def _groups() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["dependency-groups"]


def _pinned() -> str:
    """The one towncrier pin: this project's, which the action installs from."""
    (requirement,) = _groups()["release-plan"]
    return requirement.removeprefix("towncrier==")


def _plan_step() -> dict:
    steps = yaml.safe_load(ACTION.read_text())["runs"]["steps"]
    (step,) = [step for step in steps if step.get("id") == "plan"]
    return step
