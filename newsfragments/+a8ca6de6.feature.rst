Added ``uv-pytest`` and ``pipenv-pytest`` composite actions running pytest under
``coverage run``, and a ``coverage-mode: coverage-run`` option on the
``tests-pytests`` shared workflow. Both measure code imported while pytest starts
up, which ``pytest --cov`` reports as missed - most notably a pytest plugin under
test.
