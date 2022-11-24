actions-reuse
=============

Set of reusable github actions workflows


pypi
----

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/pypi.yml@v1.5.1

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
        uses: fizyk/actions-reuse/.github/workflows/linters-python.yml@v1.5.1

Lints python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv
     - false
     - Whether to use pipenv or not
   * - pipenv-install-options
     - ""
     - Additional pipenv install options
   * - requirements
     - requirements-lint.txt
     - Requirements file name
   * - python-version
     - 3.11
     - Python version to run linters on
   * - pydocstyle
     - true
     - Flag to run pydocstyle on code or not
   * - pydocstyle-paths
     - .
     - Path to run pydocstyle on
   * - pycodestyle
     - true
     - Flag to run pycodestyle on code or not
   * - pycodestyle-paths
     - .
     - Path to run pycodestyle on
   * - black
     - true
     - Flag to run black on code or not
   * - black-paths
     - .
     - Path to run black on
   * - mypy
     - false
     - Flag to run mypy on code or not
   * - mypy-paths
     - .
     - Path to run mypy on
   * - pylint
     - false
     - Flag to run pylint on code or not
   * - pylint-paths
     - .
     - Path to run pylint on
   * - rst
     - false
     - Flag to run rst on code or not
   * - rst-paths
     - *.rst
     - Path to run rst-lint on

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
        uses: fizyk/actions-reuse/.github/workflows/tests-pytests.yml@v1.5.1

Run pytest tests on python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv
     - false
     - Whether to use pipenv or not
   * - pipenv-install-options
     - ""
     - Additional pipenv install options
   * - requirements
     - requirements-lint.txt
     - Requirements file name
   * - pytest_opts
     - ""
     - Additional pytest options
   * - python-versions
     - '["3.7", "3.8", "3.9", "3.10", "3.11"]'
     - List of python versions matrix to run tests on. It has to be jsonified list.
   * - os:
     - ubuntu-latest
     - Operating system tests are running on


# Release

Install pipenv first,

Then run:

.. code-block::

    pipenv run tbump [NEW_VERSION]
