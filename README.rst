actions-reuse
=============

Set of reusable github actions workflows


pypi
----

.. code-block:: yaml

    jobs:
      build:
        uses: fizyk/actions-reuse/.github/workflows/pypi.yml@v1.7.1

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
     - default
     - note
   * - pypi_token
     - Pypi token used to authenticate with PyPI for upload.

linters-python
--------------

.. code-block:: yaml

    jobs:
      lint:
        uses: fizyk/actions-reuse/.github/workflows/linters-python.yml@v1.7.1

Lints python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv-install-options
     - ""
     - Additional pipenv install options
   * - requirements
     - Requirements file name, makes action install requirements with pip instead of default pipenv
   * - python-version
     - 3.11
     - Python version to run linters on
   * - pydocstyle
     - false
     - Flag to run pydocstyle on code or not
   * - pydocstyle-paths
     - .
     - Path to run pydocstyle on
   * - pycodestyle
     - false
     - Flag to run pycodestyle on code or not
   * - pycodestyle-paths
     - .
     - Path to run pycodestyle on
   * - black
     - false
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
        uses: fizyk/actions-reuse/.github/workflows/tests-pytests.yml@v1.7.1

Run pytest tests on python code


.. list-table:: Configuration
   :header-rows: 1

   * - parameter
     - default
     - note
   * - pipenv-install-options
     - ""
     - Additional pipenv install options
   * - requirements
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

automerge-shared
----------------

.. code-block:: yaml

    jobs:
      automerge:
        uses: fizyk/actions-reuse/.github/workflows/automerge-shared.yml@v1.7.1

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

# Release

Install pipenv first,

Then run:

.. code-block::

    pipenv run tbump [NEW_VERSION]
