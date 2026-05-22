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

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export@v5.1.0
      with:
        data-file: .coverage.serial
        output-file: coverage.xml


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

    - uses: fizyk/actions-reuse/.github/actions/uv-run@v5.1.0
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

    - uses: fizyk/actions-reuse/.github/actions/uv-setup@v5.1.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true


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

    - uses: fizyk/actions-reuse/.github/actions/uv@v5.1.0
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv-run@v5.1.0
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
   * - editable
     - no
     - ``false``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v5.1.0
      with:
        python-version: "3.14"
        allow-prereleases: false
        cache: true
        editable: false


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
   * - editable
     - no
     - ``false``

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pipenv@v5.1.0
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

    - uses: fizyk/actions-reuse/.github/actions/python-build@v5.1.0
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

    - uses: fizyk/actions-reuse/.github/actions/uv-build@v5.1.0
      with:
        python-version: "3.14"
