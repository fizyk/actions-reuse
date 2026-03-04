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

    - uses: fizyk/actions-reuse/.github/actions/coverage-combine-export@v4.4.2
      with:
        data-file: .coverage.serial
        output-file: coverage.xml


pip
---

Path: ``.github/actions/pip/action.yml``

Set up Python, install dependencies from requirements file, and run a command.

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
   * - requirements
     - no
     - ``requirements.txt``
   * - command
     - yes
     -

Example:

.. code-block:: yaml

    - uses: fizyk/actions-reuse/.github/actions/pip@v4.4.2
      with:
        python-version: "3.14"
        allow-prereleases: false
        requirements: requirements.txt
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv-run@v4.4.2
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv-setup@v4.4.2
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

    - uses: fizyk/actions-reuse/.github/actions/pipenv@v4.4.2
      with:
        python-version: "3.14"
        allow-prereleases: false
        command: pytest
