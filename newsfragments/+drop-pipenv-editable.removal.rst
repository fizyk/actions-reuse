Drop the ``pipenv install --editable .`` step and the inputs that drove it: ``editable`` on the ``pipenv`` and ``pipenv-setup`` actions, ``install_editable`` on ``shared-tests-pytests``.
A Pipfile says the same thing by itself - ``<project> = {path = ".", editable = true}`` under ``[packages]`` - so the input only duplicated it.
Callers still passing it have to drop the line: a reusable workflow rejects an input it does not declare.
