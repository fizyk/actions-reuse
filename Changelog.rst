Changelog
=========

.. towncrier release notes start

1.7.0 (2023-02-27)
==================

Features
--------

- Ability to store built package as pipeline artifacts. (`#90 <https://https://github.com/fizyk/actions-reuse/issues/90>`_)
- Be able to configure codecov's `fail_on_ci_error` - defaults to false. (`#91 <https://https://github.com/fizyk/actions-reuse/issues/91>`_)


1.6.4 (2022-12-21)
==================

Features
--------

- Add your info here (`#85 <https://https://github.com/fizyk/actions-reuse/issues/85>`_)


1.6.3 (2022-12-05)
==================

Features
--------

- Switch to build package building system (`#82 <https://https://github.com/fizyk/actions-reuse/issues/82>`_)


1.6.2 (2022-11-29)
==================

Bugfixes
--------

- Secrets have no type - fixed automerge-shared secrets definition. (`#79 <https://https://github.com/fizyk/actions-reuse/issues/79>`_)


Misc
----

- `#78 <https://https://github.com/fizyk/actions-reuse/issues/78>`_


1.6.1 (2022-11-29)
==================

Bugfixes
--------

- Add your info here (`#77 <https://https://github.com/fizyk/actions-reuse/issues/77>`_)


1.6.0 (2022-11-29)
==================

Features
--------

- Add `automerge-shared` shared workflow to re-usable workflows. (`#76 <https://https://github.com/fizyk/actions-reuse/issues/76>`_)


Misc
----

- `#74 <https://https://github.com/fizyk/actions-reuse/issues/74>`_, `#75 <https://https://github.com/fizyk/actions-reuse/issues/75>`_


1.5.2 (2022-11-25)
==================

Features
--------

- Removed pylint-paths parameters and now running pylint with `pylint --recursive y .` command.
  Any ignores can be set in .pylintrc file. (`#72 <https://https://github.com/fizyk/actions-reuse/issues/72>`_)


1.5.1 (2022-11-24)
==================

Bugfixes
--------

- Removed the ability to set up cover package's paths/names. use .coveragerc for that instead. (`#71 <https://https://github.com/fizyk/actions-reuse/issues/71>`_)


1.5.0 (2022-11-24)
==================

Features
--------

- Ability to set paths for linters (`#70 <https://https://github.com/fizyk/actions-reuse/issues/70>`_)


Misc
----

- `#68 <https://https://github.com/fizyk/actions-reuse/issues/68>`_, `#69 <https://https://github.com/fizyk/actions-reuse/issues/69>`_


1.4.1 (2022-11-18)
==================

Features
--------

- pipenv template, linters-python and tests-pytests accepts `pipenv-install-options`
  for additional pipenv install options. Might allow adding ie. `--skip-lock`. (`#67 <https://https://github.com/fizyk/actions-reuse/issues/67>`_)


1.4.0 (2022-11-08)
==================

Misc
----

- `#65 <https://https://github.com/fizyk/actions-reuse/issues/65>`_
