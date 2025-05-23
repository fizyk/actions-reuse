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
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v3.1.1

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - python-version
     - 3.13
     - Python version to use in the workflow


pre-commit
----------

Checks Pull Request against manual enabled pre-commit hooks.

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v3.1.1

.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - python-version
     - 3.13
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
        uses: fizyk/actions-reuse/.github/workflows/shared-pypi.yml@v3.1.1

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


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - pypi_token
     - Pypi token used to authenticate with PyPI for upload.

linters-python
--------------

.. code-block:: yaml

    jobs:
      lint:
        uses: fizyk/actions-reuse/.github/workflows/shared-linters-python.yml@v3.1.1

Lints python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv-install-options
     -
     - Additional pipenv install options
   * - cache
     - true
     - Whether to cache pythin environment
   * - requirements
     -
     - Requirements file name, makes action install requirements with pip instead of default pipenv
   * - python-version
     - 3.11
     - Python version to run linters on
   * - pydocstyle
     - false
     - Flag to run pydocstyle on code or not
   * - pydocstyle-paths
     - `.`
     - Path to run pydocstyle on
   * - pycodestyle
     - false
     - Flag to run pycodestyle on code or not
   * - pycodestyle-paths
     - `.`
     - Path to run pycodestyle on
   * - black
     - false
     - Flag to run black on code or not
   * - black-paths
     - `.`
     - Path to run black on
   * - mypy
     - false
     - Flag to run mypy on code or not
   * - mypy-paths
     - `.`
     - Path to run mypy on
   * - pylint
     - false
     - Flag to run pylint on code or not
   * - rst
     - false
     - Flag to run rst on code or not
   * - rst-paths
     - `*.rst`
     - Path to run rst-lint on
   * - rstcheck
     - false
     - Flag to run rstcheck on rst file or not
   * - ruff
     - false
     - Flag to run ruff on code or not
   * - ruff-paths
     - `.`
     - Path to run ruff on


tests-pytests
-------------

.. code-block:: yaml

    jobs:
      tests:
        uses: fizyk/actions-reuse/.github/workflows/shared-tests-pytests.yml@v3.1.1

Run pytest tests on python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv-install-options
     -
     - Additional pipenv install options
   * - cache
     - true
     - Whether to cache pythin environment
   * - requirements
     -
     - Requirements file name
   * - pytest_opts
     -
     - Additional pytest options
   * - python-versions
     - '["3.7", "3.8", "3.9", "3.10", "3.11"]'
     - List of python versions matrix to run tests on. It has to be jsonified list.
   * - os:
     - ubuntu-latest
     - Operating system tests are running on
   * - fail_on_codecov_error:
     - false
     - Whether pipeline should fail if there would be an error on codecov side.


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - required
     - note
   * - codecov_token
     - no
     - Codecov token

automerge
---------

.. code-block:: yaml

    jobs:
      automerge:
        uses: fizyk/actions-reuse/.github/workflows/shared-automerge.yml@v3.1.1

Runs automerge for dependabot pull requests using:

* `ridedott/merge-me-action <https://github.com/ridedott/merge-me-action>_` to run the merge
* `tibdex/github-app-token <https://github.com/tibdex/github-app-token>`_ to generate short-lived github app token with enough permissions to run the merge.

Mind that dependabot pull requests are treated as 3rd party pull requests, hence default GITHUB_TOKEN will only have read permissions.

Requires Github application to run!


.. list-table:: Configuration
   :header-rows: 1

   * - secret
     - note
   * - app_id
     - Github Application ID that'll be used for merging
   * - private_key
     - Github Application's private key

Release
-------

Install pipenv first,

Then run:

.. code-block:: sh

    pipenv run tbump [NEW_VERSION]
