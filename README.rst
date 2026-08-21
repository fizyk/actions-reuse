actions-reuse
=============

Set of reusable github actions workflows

pr-check
--------

Checks Pull Request for the added towncrier newsfragment if PR is not performed by a bot, and every Pull Request
if tbump is correctly configured according to new codebase.

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v5.5.0

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - python-version
     - 3.14
     - Python version to use in the workflow
   * - dependency-manager
     - pipenv
     - Dependency manager to use (``pipenv``, ``uv``)


pre-commit
----------

Checks Pull Request against manual enabled pre-commit hooks.

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v5.5.0

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - python-version
     - 3.14
     - Python version to use in the workflow

To configure pre-commit hooks to be run with this workflow, add stages parameter:

.. code-block:: yaml

  - repo: local
    hooks:
      - id: pipenv
        stages: [pre-commit, manual]


pypi
----

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/shared-pypi.yml@v5.5.0

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - publish
     - false
     - Whether to publish package to pypi or not
   * - artifact
     - false
     - Whether to upload built packages as pipeline artifacts or not
   * - python-version
     - "3.14"
     - Python version used to build the distributions
   * - dependency-manager
     - build
     - Build tool to use (``build`` uses ``python -m build``; ``uv`` uses ``uv build``)


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - pypi_token
     - Pypi token used to authenticate with PyPI for upload.


tests-pytests
-------------

.. code-block:: yaml

    jobs:
      tests:
        uses: fizyk/actions-reuse/.github/workflows/shared-tests-pytests.yml@v5.5.0

Run pytest tests on python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - dependency-manager
     - pipenv
     - Dependency manager to use (``pipenv``, ``uv``)
   * - pipenv-install-options
     -
     - Additional pipenv install options (pipenv only)
   * - cache
     - true
     - Whether to cache python environment
   * - pytest_opts
     -
     - Additional pytest options
   * - python-versions
     - '["3.10", "3.11", "3.12", "3.13", "3.14"]'
     - List of python versions matrix to run tests on. It has to be jsonified list.
   * - allow-prereleases
     - true
     - "Allow falling back to pre-release versions of Python when a matching GA version of Python is not available."
   * - os
     - ubuntu-latest
     - Operating system tests are running on
   * - env
     - {}
     - JSON object string of environment variables to set
   * - fail_on_codecov_error
     - false
     - Whether pipeline should fail if there would be an error on codecov side.
   * - coverage-run-mode
     - false
     - Run pytest under ``coverage run`` instead of ``pytest --cov``. See below.
   * - coverage-process-start
     -
     - Coverage configuration file read by child processes. Set it only for a suite that spawns any - xdist workers, subprocesses - and have it enable ``parallel`` and set ``patch = subprocess``. Empty means a single process, needing no coverage configuration. ``coverage-run-mode`` only.


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - required
     - note
   * - codecov_token
     - no
     - Codecov token

Testing a pytest plugin
+++++++++++++++++++++++

``pytest --cov`` starts measuring coverage after pytest imported its entry point
plugins, so for a project that *is* a pytest plugin every import time line of the
plugin - imports, ``def``, ``class``, decorators, constants - is reported as
missed. Rather than working around it in the test suite with ``-p no:myplugin``
plus a ``pytest_plugins`` entry in ``conftest.py``, switch the engine:

.. code-block:: yaml

    jobs:
      tests:
        uses: fizyk/actions-reuse/.github/workflows/shared-tests-pytests.yml@v5.5.0
        with:
          dependency-manager: 'uv'
          coverage-run-mode: true
        secrets:
          codecov_token: ${{ secrets.CODECOV_TOKEN }}

``coverage run -m pytest`` starts before pytest is imported and sees those lines.
``pytest-cov`` stays installed, it just no longer drives the parent process, so
``--cov`` must not be passed in ``pytest_opts``. That is all a single-process
suite needs. A suite that spawns child processes - xdist workers, or code under
test starting subprocesses - additionally sets ``coverage-process-start`` to a
coverage configuration enabling ``parallel`` and ``patch = subprocess``, so those
processes are measured too; see `ACTIONS.rst <ACTIONS.rst>`__ for why both, and
pass an absolute path there if the tests change the working directory.

This workflow runs pytest once per job. Projects needing steps in between - a
database service to set up, a binary to detect - or several pytest runs per job -
a serial pass next to an xdist one - should compose the
``uv-pytest-coverage``/``pipenv-pytest-coverage`` composite actions in their own job instead, which
pays for environment setup once rather than once per run. See
`ACTIONS.rst <ACTIONS.rst>`__.

diagrams
--------

.. code-block:: yaml

    name: Render Mermaid Diagrams
    on:
      push:
        paths:
          - 'docs/*.mmd' # Trigger only when mermaid files change
          - '.github/workflows/diagram.yml'

    jobs:
      diagrams:
        # Grant the action permission to write to the repository
        permissions:
          contents: write
        uses: fizyk/actions-reuse/.github/workflows/shared-diagrams.yml@v5.5.0


Generates svg images out of the mmd diagrams

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - mmd_path
     - docs
     - Location of the Mermaid Markdown file
   * - svg_path
     - docs/images
     - Location of the path to generate svg files to
   * - puppeteer_config
     - docs/puppeteer-config.json
     - Path to puppeteer config file
   * - skip_ci
     - false
     - Whether autogenerated diagram commit message should include ``[skip ci]``.

automerge
---------

.. code-block:: yaml

    name: Merge me test dependencies!

    on:
      pull_request_target:
        types: [opened, reopened, synchronize]

    jobs:
      automerge:
        uses: fizyk/actions-reuse/.github/workflows/shared-automerge.yml@v5.5.0

Arms `GitHub's native auto-merge <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request>`_ on dependabot and pre-commit.ci pull requests, using
`actions/create-github-app-token <https://github.com/actions/create-github-app-token>`_ to generate a short-lived github app token with enough permissions to enable it.

Mind that dependabot pull requests are treated as 3rd party pull requests, hence default GITHUB_TOKEN will only have read permissions.

Requires Github application to run!

**Requires** ``allow_auto_merge`` to be enabled on the calling repository, otherwise enabling auto-merge fails::

    gh api -X PATCH repos/OWNER/REPO -F allow_auto_merge=true

Major version bumps are left alone; patch and minor bumps are armed. Pull requests with no approving review are approved first, so repositories requiring approvals keep merging dependency updates while still holding human pull requests.

Prefer ``pull_request_target``: arming is a one-shot action, and GitHub merges once the last required check reports, whichever API it reports through. It arms as the pull request opens, which assumes required status checks are configured. ``workflow_run`` and ``check_suite`` completion also work, but run the job once per finished check. On any other event the job is skipped.

Do not use ``pull_request``: dependabot runs get no repository secrets there, so the app token cannot be minted.


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - client_id
     - Github Application Client ID that'll be used for merging
   * - private_key
     - Github Application's private key

release
-------

.. code-block:: yaml

    name: Release
    on:
      workflow_dispatch:
        inputs:
          version:
            description: 'New version to be added'
            required: true
            type: string
    jobs:
      release:
        # The bump commit and the tag are pushed with the app token, not with
        # the job's GITHUB_TOKEN, so reading is all this job needs.
        permissions:
          contents: read
        uses: fizyk/actions-reuse/.github/workflows/shared-release.yml@v5.5.0
        with:
          version: ${{ inputs.version }}

Runs release on a repository. Requires tbump to be installed and configured in dependencies.

The app token is minted with only the permissions the release needs, so the Github
application has to grant all three: *Contents: write* for the bump commit and the tag,
*Metadata: read*, and *Workflows: write*. The last one is requested unconditionally and
minting the token fails without it, so it is required even when the repository keeps no
workflows - a push touching ``.github/workflows`` is rejected without it anyway.

The version passed in has to look like a version (``[0-9A-Za-z.+-]``): it reaches tbump
through a shell command, and this workflow holds the release credentials.


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - note
   * - version
     - Required to be passed

.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - app_id
     - Github Application ID that'll be used for releasing
   * - private_key
     - Github Application's private key

release-schedule
----------------

.. code-block:: yaml

    name: Scheduled release
    on:
      schedule:
        - cron: '17 6 1 * *'
        - cron: '17 6 * * 1'
      workflow_dispatch: {}

    jobs:
      schedule:
        uses: fizyk/actions-reuse/.github/workflows/shared-release-schedule.yml@v5.5.0
        with:
          dependency-manager: 'uv'
        secrets:
          app_id: ${{ secrets.RELEASE_APP_ID }}
          private_key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}

Computes the next version and, if warranted, runs the ``release`` workflow on a schedule
(and on demand via ``workflow_dispatch``). Because ``schedule`` triggers only fire from
a workflow file present on the repository's default branch, this caller has to live
in each repository - copy the snippet above and pin it to a tag.

The next version is derived from the latest ``vX.Y.Z``/``X.Y.Z`` git tag: a release is
only planned when there are commits since that tag. The bump level follows the towncrier
types present - *major* for a type listed in ``major-fragments``, else *minor* for one
listed in ``minor-fragments``, else *patch*. Requires tbump to be installed and
configured, and a towncrier newsfragments directory.

Planning is done by the `release-plan <ACTIONS.rst>`__ action, which reads the
repository's towncrier configuration and classifies fragments with towncrier's own
parser. The fragments directory and the fragment types - custom ones included - are
whatever the repository already declares, so there is nothing to repeat here; and every
name towncrier accepts is recognised, including its counter form (``790.feature.1.rst``)
and extension-less fragments (``790.feature``).

On a pre-1.0 project a breaking change should raise the minor, so leave
``major-fragments`` empty and list the breaking type under ``minor-fragments``::

    with:
      minor-fragments: 'feature,break'

With ``newsfragments-required`` enabled an empty newsfragments directory skips quietly
and successfully. A missing directory fails the run, and so does a directory holding
only files that no fragment type claims - such a repository would never release.


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - dependency-manager
     - pipenv
     - Dependency manager to use (``pipenv``, ``uv``)
   * - newsfragments-required
     - false
     - Only release when at least one towncrier newsfragment is present
   * - minor-fragments
     - feature
     - Comma-separated towncrier types that trigger a minor bump
   * - major-fragments
     -
     - Comma-separated towncrier types that trigger a major bump. Leave empty on pre-1.0 projects

.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - app_id
     - Github Application ID that'll be used for releasing
   * - private_key
     - Github Application's private key

Python versions
---------------

Available python versions can be checked in `https://github.com/actions/python-versions?tab=readme-ov-file#python-for-actions <actions/python-versions>`__ repository.

Release
-------

Install uv first (https://docs.astral.sh/uv/getting-started/installation/),

Then run:

.. code-block:: sh

    uv run tbump [NEW_VERSION]

Tests
-----

Composite actions that carry logic of their own are unit tested. Install uv, then run:

.. code-block:: sh

    uv sync --all-groups
    uv run pytest

The suite runs in CI through this repository's own ``tests-pytests`` workflow.
``release-plan`` installs the towncrier version pinned here rather than carrying a pin of
its own, so a dependabot bump of towncrier exercises the planner against the version the
action actually ships - which is what makes the planner's use of towncrier's private API
tolerable.

Composite actions
-----------------

See `ACTIONS.rst <ACTIONS.rst>`__ for documentation of available composite actions.
