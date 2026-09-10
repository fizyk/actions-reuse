Composite Actions
=================

This repository provides the following reusable composite actions.

coverage-combine-export
-----------------------

Path: ``.github/actions/coverage-combine-export/action.yml``

Combine coverage files and export a single XML report.

``coverage combine`` discovers the ``<data-file>.*`` files a parallel run wrote,
so the run being combined has to have ``parallel`` enabled in its coverage
configuration - without it there is nothing to combine and the step fails, which
is the right answer, because xdist workers would have been overwriting each
other's data anyway.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - note
   * - data-file
     - yes
     - Coverage data file prefix (for example ``.coverage.serial``)
   * - output-file
     - yes
     - XML output filename

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export@v5.7.0
      with:
        data-file: .coverage.serial
        output-file: coverage.xml


coverage-combine-export-uv
--------------------------

Path: ``.github/actions/coverage-combine-export-uv/action.yml``

Combine coverage files and export a single XML report using uv.

``coverage combine`` discovers the ``<data-file>.*`` files a parallel run wrote,
so the run being combined has to have ``parallel`` enabled in its coverage
configuration - without it there is nothing to combine and the step fails, which
is the right answer, because xdist workers would have been overwriting each
other's data anyway.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - note
   * - data-file
     - yes
     - Coverage data file prefix (for example ``.coverage.serial``)
   * - output-file
     - yes
     - XML output filename

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export-uv@v5.7.0
      with:
        data-file: .coverage.serial
        output-file: coverage.xml


release-plan
------------

Path: ``.github/actions/release-plan/action.yml``

Decide whether a release is warranted and compute the next version. The bump level
follows the towncrier newsfragments present: *major* for a type listed in
``major-fragments``, else *minor* for one listed in ``minor-fragments``, else *patch*.

The fragments directory and the fragment types are read from the repository's own
towncrier configuration, and every filename is classified by towncrier's parser, so
custom types, sections, markdown fragments, the counter form (``790.feature.1.rst``)
and extension-less fragments (``790.feature``) all work without configuring anything
twice. Used by the ``release-schedule`` workflow; needs a checkout with tags
(``fetch-depth: 0``, ``fetch-tags: true``).

The planner reads towncrier's private API, so it installs the towncrier version pinned
in ``actions-reuse``'s own ``pyproject.toml`` - which is also the version this
repository's test suite runs against. There is no version input: a second pin could
drift from the one being tested.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - newsfragments-required
     - no
     - ``false``
   * - minor-fragments
     - no
     - ``feature``
   * - major-fragments
     - no
     - ``""``
   * - python-version
     - no
     - ``3.14``

.. list-table:: Outputs
   :header-rows: 1

   * - output
     - note
   * - should_release
     - ``true`` when a release should be made
   * - version
     - The next version, set only when ``should_release`` is ``true``

Example:

.. code-block:: yaml

    - id: plan
      uses: fizyk/actions-reuse/.github/actions/release-plan@v5.7.0
      with:
        minor-fragments: 'feature,break'


mermaid-render
--------------

Path: ``.github/actions/mermaid-render/action.yml``

Render every ``.mmd`` file in a directory to SVG. Used by the ``diagram`` workflow.

The renderer is installed with ``npm ci`` from the ``package-lock.json`` committed
next to the action, so no mermaid-cli release redraws a caller's diagrams by itself;
dependabot's ``npm`` ecosystem raises the pin here. The lockfile sits beside the
action because the job runs against the caller's checkout, which holds no Node
manifest. ``node_modules`` lands under ``$GITHUB_ACTION_PATH``, so the only thing
written into that checkout is the SVGs under ``svg-path``.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - mmd-path
     - no
     - ``docs``
   * - svg-path
     - no
     - ``docs/images``
   * - puppeteer-config
     - no
     - ``docs/puppeteer-config.json``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/mermaid-render@v5.7.0
      with:
        mmd-path: docs
        svg-path: docs/images


uv-run
------

Path: ``.github/actions/uv-run/action.yml``

Run a command inside an existing uv environment.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - command
     - yes
     -
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-run@v5.7.0
      with:
        command: pytest -q
        env: '{"PYTEST_ADDOPTS":"-ra"}'


uv-setup
--------

Path: ``.github/actions/uv-setup/action.yml``

Set up Python and uv, then install project dependencies via ``uv sync --all-groups``.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -
   * - allow-prereleases
     - yes
     -
   * - uv-install-options
     - no
     - ``""``
   * - cache
     - no
     - ``true``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-setup@v5.7.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true


uv-pip
------

Path: ``.github/actions/uv-pip/action.yml``

Install packages into the environment ``uv-setup`` prepared, using
``uv pip install`` - to override locked versions, such as the oldest supported
dependencies.

Prefer it to ``uv-run`` with a ``pip install`` command. uv does not seed ``pip``
into the environments it creates, so ``uv run pip`` finds whatever ``pip`` sits
on ``PATH`` and installs into that interpreter instead of the project
environment - without failing, wherever such a ``pip`` exists.

Set ``UV_NO_SYNC`` for the job as well, or the next ``uv run`` re-syncs from the
lockfile and reverts what was installed here; the action warns when it is unset.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - requirements
     - no
     - ``""``
   * - packages
     - no
     - ``""``

At least one of the two is required. ``packages`` is split on whitespace and
needs no shell quoting of its own, so a single specifier must not contain
spaces: write ``elasticsearch<9``, not ``elasticsearch < 9``.

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-pip@v5.7.0
      with:
        requirements: oldest/requirements.txt

    - uses: fizyk/actions-reuse/.github/actions/uv-pip@v5.7.0
      with:
        packages: elasticsearch<9


uv-pytest-coverage
------------------

Path: ``.github/actions/uv-pytest-coverage/action.yml``

Run pytest under ``coverage run`` in an environment already prepared by
``uv-setup``, then export the XML report, combining the data files first when
the run spawned child processes.

Use it instead of ``pytest --cov`` when the code under test is imported while
pytest starts up - a pytest plugin loaded through an entry point. ``pytest-cov``
starts measuring after those imports happened, so it reports every import time
line of the plugin as missed. ``coverage run`` starts before pytest is imported
at all and sees them. Subprocesses and xdist workers stay measured because this
action sets ``COVERAGE_PROCESS_START``, which starts coverage in every child
process. Do not pass ``--cov`` in ``pytest-opts``:
together with the ``COVERAGE_PROCESS_START`` this action sets, it puts two
coverage engines on one process, which warns and can interfere with what gets
collected.

A single-process suite needs nothing else: leave ``coverage-config``
empty and the action runs pytest and writes the XML.

A suite that spawns child processes - xdist workers, or code under test starting
subprocesses - sets ``coverage-config`` to a coverage configuration that
enables ``parallel`` and sets ``patch = subprocess``
(``patch = ["subprocess"]`` in ``pyproject.toml``):

.. code-block:: ini

    [run]
    parallel = true
    patch = subprocess

Each process then writes its own data file and the action combines them before
exporting. It is also passed to the parent as ``coverage run --rcfile``, so
parent and children read the same settings even when the file is not at a name
coverage discovers by itself.

Pass ``coverage-config`` and ``data-file`` as absolute paths if the tests
change the working directory - with ``tmp_path``, ``monkeypatch.chdir`` or the
like. Child processes inherit that directory, and relative paths would have them
look for the configuration, and write their data, somewhere the combine step
never reads.

``patch`` is what makes ``COVERAGE_PROCESS_START`` take effect on its own.
Coverage ships an ``a1_coverage.pth`` hook that does the same job, but only
since coverage 7.13, and ``pytest-cov`` dropped the ``.pth`` it used to ship in
its 7.0 release. So on coverage 7.10.6 to 7.12 paired with ``pytest-cov`` 7 -
a combination its own dependency floor allows - neither hook is installed, and
without ``patch`` every subprocess and xdist worker goes unmeasured while the
run still passes. Setting it is harmless on newer coverage.

Use the action once per pytest run, giving each run its own ``data-file`` and
``output-file``, and upload every resulting XML in a single Codecov step. Runs do
not interfere with each other: the combine step picks up only the
``<data-file>.*`` files its own run wrote.

Coverage is combined and exported even when the tests failed.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - pytest-opts
     - no
     - ``""``
   * - data-file
     - no
     - ``.coverage``
   * - output-file
     - no
     - ``coverage.xml``
   * - coverage-config
     - no
     - ``""``
   * - env
     - no
     - ``{}``

``env`` is a JSON object string, as everywhere else here. The coverage variables
the action sets are merged into it and win over it, so leave ``COVERAGE_FILE``
and ``COVERAGE_PROCESS_START`` out.

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-setup@v5.7.0
      with:
        python-version: "3.14"
    - uses: fizyk/actions-reuse/.github/actions/uv-pytest-coverage@v5.7.0
      with:
        pytest-opts: -n auto --dist loadgroup --max-worker-restart 0
        data-file: .coverage.xdist
        output-file: coverage-xdist.xml


uv
--

Path: ``.github/actions/uv/action.yml``

Set up uv and run a command in one step.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -
   * - allow-prereleases
     - yes
     -
   * - command
     - yes
     -
   * - uv-install-options
     - no
     - ``""``
   * - cache
     - no
     - ``true``
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv@v5.7.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        command: pytest


pipenv-run
----------

Path: ``.github/actions/pipenv-run/action.yml``

Run a command inside an existing pipenv environment.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - command
     - yes
     -
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv-run@v5.7.0
      with:
        command: pytest -q
        env: '{"PYTEST_ADDOPTS":"-ra"}'


pipenv-setup
------------

Path: ``.github/actions/pipenv-setup/action.yml``

Set up Python and pipenv, then install project dependencies.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -
   * - allow-prereleases
     - yes
     -
   * - pipenv-install-options
     - no
     - ``""``
   * - cache
     - no
     - ``true``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v5.7.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true


pipenv-pytest-coverage
----------------------

Path: ``.github/actions/pipenv-pytest-coverage/action.yml``

Run pytest under ``coverage run`` in an environment already prepared by
``pipenv-setup``, then export the XML report, combining the data files first when
the run spawned child processes.

Use it instead of ``pytest --cov`` when the code under test is imported while
pytest starts up - a pytest plugin loaded through an entry point. ``pytest-cov``
starts measuring after those imports happened, so it reports every import time
line of the plugin as missed. ``coverage run`` starts before pytest is imported
at all and sees them. Subprocesses and xdist workers stay measured because this
action sets ``COVERAGE_PROCESS_START``, which starts coverage in every child
process. Do not pass ``--cov`` in ``pytest-opts``:
together with the ``COVERAGE_PROCESS_START`` this action sets, it puts two
coverage engines on one process, which warns and can interfere with what gets
collected.

A single-process suite needs nothing else: leave ``coverage-config``
empty and the action runs pytest and writes the XML.

A suite that spawns child processes - xdist workers, or code under test starting
subprocesses - sets ``coverage-config`` to a coverage configuration that
enables ``parallel`` and sets ``patch = subprocess``
(``patch = ["subprocess"]`` in ``pyproject.toml``):

.. code-block:: ini

    [run]
    parallel = true
    patch = subprocess

Each process then writes its own data file and the action combines them before
exporting. It is also passed to the parent as ``coverage run --rcfile``, so
parent and children read the same settings even when the file is not at a name
coverage discovers by itself.

Pass ``coverage-config`` and ``data-file`` as absolute paths if the tests
change the working directory - with ``tmp_path``, ``monkeypatch.chdir`` or the
like. Child processes inherit that directory, and relative paths would have them
look for the configuration, and write their data, somewhere the combine step
never reads.

``patch`` is what makes ``COVERAGE_PROCESS_START`` take effect on its own.
Coverage ships an ``a1_coverage.pth`` hook that does the same job, but only
since coverage 7.13, and ``pytest-cov`` dropped the ``.pth`` it used to ship in
its 7.0 release. So on coverage 7.10.6 to 7.12 paired with ``pytest-cov`` 7 -
a combination its own dependency floor allows - neither hook is installed, and
without ``patch`` every subprocess and xdist worker goes unmeasured while the
run still passes. Setting it is harmless on newer coverage.

Use the action once per pytest run, giving each run its own ``data-file`` and
``output-file``, and upload every resulting XML in a single Codecov step. Runs do
not interfere with each other: the combine step picks up only the
``<data-file>.*`` files its own run wrote.

Coverage is combined and exported even when the tests failed.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - pytest-opts
     - no
     - ``""``
   * - data-file
     - no
     - ``.coverage``
   * - output-file
     - no
     - ``coverage.xml``
   * - coverage-config
     - no
     - ``""``
   * - env
     - no
     - ``{}``

``env`` is a JSON object string, as everywhere else here. The coverage variables
the action sets are merged into it and win over it, so leave ``COVERAGE_FILE``
and ``COVERAGE_PROCESS_START`` out.

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v5.7.0
      with:
        python-version: "3.14"
    - uses: fizyk/actions-reuse/.github/actions/pipenv-pytest-coverage@v5.7.0
      with:
        pytest-opts: -n auto --dist loadgroup --max-worker-restart 0
        data-file: .coverage.xdist
        output-file: coverage-xdist.xml


pipenv
------

Path: ``.github/actions/pipenv/action.yml``

Set up pipenv and run a command in one step.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -
   * - allow-prereleases
     - yes
     -
   * - command
     - yes
     -
   * - pipenv-install-options
     - no
     - ``""``
   * - cache
     - no
     - ``true``
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv@v5.7.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        command: pytest


python-build
------------

Path: ``.github/actions/python-build/action.yml``

Build Python distributions using the pypa ``build`` frontend (``python -m build``) and validate the result with ``twine check``.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/python-build@v5.7.0
      with:
        python-version: "3.14"


uv-build
--------

Path: ``.github/actions/uv-build/action.yml``

Build Python distributions using ``uv build`` and validate the result with ``uvx twine check``.

.. list-table:: Inputs
   :header-rows: 1

   * - input
     - required
     - default
   * - python-version
     - yes
     -

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-build@v5.7.0
      with:
        python-version: "3.14"
