actions-reuse
=============

Set of reusable github actions workflows


pypi
----

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/pypi.yml@main

Has optional parameter **publish** and optional secret **pypi_token**

Without these parameters, this workflow only builds and validates package.
With them, it also publishes the package to pypi.

.. code-block:: yaml

    with:
      publish: true
    secrets:
      pypi_token: ${{ secrets.pypi_password }}

linters-python
--------------

.. code-block:: yaml

    jobs:
      lint:
        uses: fizyk/actions-reuse/.github/workflows/linters-python.yml@main

Lints python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - requirements
     - requirements-lint.txt
     - Requirements file name
   * - python-version
     - 3.10
     - Python version to run linters on
   * - pydocstyle
     - true
     - Flag to run pydocstyle on code or not
   * - pydocstyle
     - true
     - Flag to run pydocstyle on code or not
   * - black
     - true
     - Flag to run black on code or not
   * - mypy
     - false
     - Flag to run mypy on code or not
   * - pylint
     - false
     - Flag to run pylint on code or not

.. list-table:: linters that can be run
    :header-rows: 1

   * - linter
     - default
   * - pydocstyle
     - yes
   * - pycodestyle
     - yes
   * - black
     - yes
   * - mypy
     - no
   * - pylint
     - no

tests-pytests
-------------

.. code-block:: yaml

    jobs:
      tests:
        uses: fizyk/actions-reuse/.github/workflows/tests-pytests.yml@main

Run pytest tests on python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - requirements
     - requirements-lint.txt
     - Requirements file name
   * - cover_package
     -
     - Package name which should be covered
   * - test_path
     - tests/
     - Test path
   * - pytest_opts
     - ""
     - Additional pytest options
   * - python-versions
     - '["3.7", "3.8", "3.9", "3.10"]'
     - List of python versions matrix to run tests on. It has to be jsonified list.
