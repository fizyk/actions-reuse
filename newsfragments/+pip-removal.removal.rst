Remove ``requirements`` input and pip dependency manager path from ``shared-tests-pytests`` workflow.
Projects using ``requirements:`` should migrate to uv (``dependency-manager: uv``) or pipenv.
