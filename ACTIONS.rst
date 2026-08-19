Composite Actions
=================

This repository provides the following reusable composite actions.

coverage-combine-export
-----------------------

Path: ``.github/actions/coverage-combine-export/action.yml``

Combine coverage files and export a single XML report.

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

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export@v5.5.0
      with:
        data-file: .coverage.serial
        output-file: coverage.xml


coverage-combine-export-uv
--------------------------

Path: ``.github/actions/coverage-combine-export-uv/action.yml``

Combine coverage files and export a single XML report using uv.

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

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export-uv@v5.5.0
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
      uses: fizyk/actions-reuse/.github/actions/release-plan@v5.5.0
      with:
        minor-fragments: 'feature,break'


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

    - uses: fizyk/actions-reuse/.github/actions/uv-run@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/uv-setup@v5.5.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true


uv-pytest
---------

Path: ``.github/actions/uv-pytest/action.yml``

Run pytest under ``coverage run`` in an environment already prepared by
``uv-setup``, then combine the data files and export the XML report.

Use it instead of ``pytest --cov`` when the code under test is imported while
pytest starts up - a pytest plugin loaded through an entry point. ``pytest-cov``
starts measuring after those imports happened, so it reports every import time
line of the plugin as missed. ``coverage run`` starts before pytest is imported
at all and sees them. ``pytest-cov`` is still needed and still used: its ``.pth``
hook starts coverage in xdist workers and other subprocesses whenever
``COVERAGE_PROCESS_START`` is set, which this action sets. Do not pass ``--cov``
in ``pytest-opts`` - two coverage engines on one process only warn at each other.

The coverage configuration file pointed at by ``coverage-process-start`` has to
enable ``parallel``, otherwise workers overwrite each other's data.

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
   * - coverage-process-start
     - no
     - ``.coveragerc``
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/uv-setup@v5.5.0
      with:
        python-version: "3.14"
    - uses: fizyk/actions-reuse/.github/actions/uv-pytest@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/uv@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv-run@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v5.5.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true


pipenv-pytest
-------------

Path: ``.github/actions/pipenv-pytest/action.yml``

Run pytest under ``coverage run`` in an environment already prepared by
``pipenv-setup``, then combine the data files and export the XML report.

Use it instead of ``pytest --cov`` when the code under test is imported while
pytest starts up - a pytest plugin loaded through an entry point. ``pytest-cov``
starts measuring after those imports happened, so it reports every import time
line of the plugin as missed. ``coverage run`` starts before pytest is imported
at all and sees them. ``pytest-cov`` is still needed and still used: its ``.pth``
hook starts coverage in xdist workers and other subprocesses whenever
``COVERAGE_PROCESS_START`` is set, which this action sets. Do not pass ``--cov``
in ``pytest-opts`` - two coverage engines on one process only warn at each other.

The coverage configuration file pointed at by ``coverage-process-start`` has to
enable ``parallel``, otherwise workers overwrite each other's data.

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
   * - coverage-process-start
     - no
     - ``.coveragerc``
   * - env
     - no
     - ``{}``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v5.5.0
      with:
        python-version: "3.14"
    - uses: fizyk/actions-reuse/.github/actions/pipenv-pytest@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/python-build@v5.5.0
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

    - uses: fizyk/actions-reuse/.github/actions/uv-build@v5.5.0
      with:
        python-version: "3.14"
