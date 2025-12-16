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
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v4.1.1

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
        uses: fizyk/actions-reuse/.github/workflows/shared-pr-check.yml@v4.1.1

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
        uses: fizyk/actions-reuse/.github/workflows/shared-pypi.yml@v4.1.1

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


tests-pytests
-------------

.. code-block:: yaml

    jobs:
      tests:
        uses: fizyk/actions-reuse/.github/workflows/shared-tests-pytests.yml@v4.1.1

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
     - '["3.10", "3.11", "3.12", "3.13", "3.14"]'
     - List of python versions matrix to run tests on. It has to be jsonified list.
   * - allow-prereleases
     - true
     - "Allow falling back to pre-release versions of Python when a matching GA version of Python is not available."
   * - os:
     - ubuntu-latest
     - Operating system tests are running on
   * - env
     - {}
     - 'JSON object string of environment variables to set (only for pipenv path)'
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
        uses: fizyk/actions-reuse/.github/workflows/shared-automerge.yml@v4.1.1

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

Python versions
---------------

Available python versions can be checked in `https://github.com/actions/python-versions?tab=readme-ov-file#python-for-actions <actions/python-versions>`__ repository.

Release
-------

Install pipenv first,

Then run:

.. code-block:: sh

    pipenv run tbump [NEW_VERSION]
