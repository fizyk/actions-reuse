Added ``uv-pytest`` and ``pipenv-pytest`` composite actions running pytest under
``coverage run``, and a ``coverage-run-mode`` option on the
``tests-pytests`` shared workflow. Both measure code imported while pytest starts
up, which ``pytest --cov`` reports as missed - most notably a pytest plugin under
test. The coverage configuration they point at has to enable ``parallel`` and set
``patch = subprocess``, the latter because ``pytest-cov`` 7 dropped the ``.pth``
hook that used to start coverage in subprocesses and xdist workers.
