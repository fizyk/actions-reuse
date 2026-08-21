Added ``uv-pytest-coverage`` and ``pipenv-pytest-coverage`` composite actions running pytest under
``coverage run``, and a ``coverage-run-mode`` option on the
``tests-pytests`` shared workflow. Both measure code imported while pytest starts
up, which ``pytest --cov`` reports as missed - most notably a pytest plugin under
test. A suite that spawns child processes - xdist
workers, subprocesses - additionally points ``coverage-process-start`` at a coverage
configuration enabling ``parallel`` and ``patch = subprocess``, the latter because
``pytest-cov`` 7 dropped the ``.pth`` hook that used to start coverage in them.
