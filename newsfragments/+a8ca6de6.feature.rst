Add ``uv-pytest-coverage`` and ``pipenv-pytest-coverage`` actions, and
``coverage-run-mode`` on the ``tests-pytests`` workflow, running pytest under
``coverage run`` so a plugin under test gets the lines it imports at startup
measured - which ``pytest --cov`` misses.
