Changelog
=========

.. towncrier release notes start

2.5.1 (2025-02-03)
==================

Bugfixes
--------

- Fixed paramter for tunring on/off pre-commit linter.


2.5.0 (2025-01-30)
==================

Features
--------

- Ability to run pre-commit


Misc
----

- Do not use --skip-lock flag in scripts.


2.4.8 (2024-10-09)
==================

Features
--------

- Moved most of the default Python version to 3.13
  Dropped python 3.8 from default set of pythons


2.4.7 (2024-05-08)
==================

Misc
----

- `#173 <https:/github.com/fizyk/actions-reuse/issues/173>`_


2.4.6 (2024-05-08)
==================

Misc
----

- `#172 <https:/github.com/fizyk/actions-reuse/issues/172>`_


2.4.5 (2024-05-08)
==================

Misc
----

- `#171 <https:/github.com/fizyk/actions-reuse/issues/171>`_


2.4.4 (2024-03-15)
==================

Misc
----

- `#160 <https:/github.com/fizyk/actions-reuse/issues/160>`_


2.4.3 (2024-03-15)
==================

No significant changes.


2.4.2 (2023-10-26)
==================

Features
--------

- Ability to make caching optional (`#140 <https:/github.com/fizyk/actions-reuse/issues/140>`_)


2.4.1 (2023-10-23)
==================

Bugfixes
--------

- If PKG_CONFIG_PATH is set, then work around setup-python and extend it with original value. (`#139 <https:/github.com/fizyk/actions-reuse/issues/139>`_)


2.4.0 (2023-10-03)
==================

Features
--------

- Use Python 3.12 by default, drop 3.7 for default set of python versions. (`#138 <https:/github.com/fizyk/actions-reuse/issues/138>`_)


2.3.2 (2023-09-11)
==================

Misc
----

- `#137 <https:/github.com/fizyk/actions-reuse/issues/137>`_


2.3.1 (2023-09-08)
==================

Bugfixes
--------

- fix pipenv caching - use Pipfile for dependency cache not Pipfile.lock which might not be present (`#133 <https:/github.com/fizyk/actions-reuse/issues/133>`_)


2.3.0 (2023-09-08)
==================

Features
--------

- Store Pipfile.lock as an artifact if it's not versioned. (`#128 <https:/github.com/fizyk/actions-reuse/issues/128>`_)
- Cache pipenv dependencies (`#129 <https:/github.com/fizyk/actions-reuse/issues/129>`_)
- Cache `Pipfile.lock` if it's not versioned in git -
  this will help provide reproducible builds, and allows
  to remove `--skip-lock` flags from pipenv install commands.. (`#129 <https:/github.com/fizyk/actions-reuse/issues/129>`_)


2.2.1 (2023-07-12)
==================

Bugfixes
--------

- Trigger rstcheck on rstcheck flag not rst one. (`#123 <https:/github.com/fizyk/actions-reuse/issues/123>`_)


2.2.0 (2023-07-12)
==================

Features
--------

- Added support for rstcheck rst linter (`#120 <https:/github.com/fizyk/actions-reuse/issues/120>`_)


Misc
----

- `#117 <https:/github.com/fizyk/actions-reuse/issues/117>`_


2.1.2 (2023-05-20)
==================

Deprecations and Removals
-------------------------

- Revert trusted publishers, it's still not supported for reusable workflows. (`#111 <https://github.com/fizyk/actions-reuse/issues/111>`_)


2.1.1 (2023-05-19)
==================

Bugfixes
--------

- Removed unneeded secrets fro pypi workflow (`#110 <https://github.com/fizyk/actions-reuse/issues/110>`_)


2.1.0 (2023-05-19)
==================

Features
--------

- Migrate pypi workflow to trusted publishers (`#109 <https://github.com/fizyk/actions-reuse/issues/109>`_)


2.0.0 (2023-05-16)
==================

Features
--------

- Added support to run ruff linter (`#97 <https://github.com/fizyk/actions-reuse/issues/97>`_)
- Have all linters turned off by default. Turning them on explicitly would be much more sane. (`#98 <https://github.com/fizyk/actions-reuse/issues/98>`_)
- Run all actions on pipenv by default instead of pip. (`#99 <https://github.com/fizyk/actions-reuse/issues/99>`_)


Deprecations and Removals
-------------------------

- Removed pipenv option. Now pipenv is used by default and actions only fall back to pip if requirements file is being passed. (`#99 <https://github.com/fizyk/actions-reuse/issues/99>`_)


1.7.1 (2023-03-06)
==================

Bugfixes
--------

- Fix incorrect parameter type bool -> boolean (`#92 <https://github.com/fizyk/actions-reuse/issues/92>`_)


1.7.0 (2023-02-27)
==================

Features
--------

- Ability to store built package as pipeline artifacts. (`#90 <https://github.com/fizyk/actions-reuse/issues/90>`_)
- Be able to configure codecov's `fail_on_ci_error` - defaults to false. (`#91 <https://github.com/fizyk/actions-reuse/issues/91>`_)


1.6.4 (2022-12-21)
==================

Features
--------

- Add your info here (`#85 <https://github.com/fizyk/actions-reuse/issues/85>`_)


1.6.3 (2022-12-05)
==================

Features
--------

- Switch to build package building system (`#82 <https://github.com/fizyk/actions-reuse/issues/82>`_)


1.6.2 (2022-11-29)
==================

Bugfixes
--------

- Secrets have no type - fixed automerge-shared secrets definition. (`#79 <https://github.com/fizyk/actions-reuse/issues/79>`_)


Misc
----

- `#78 <https://github.com/fizyk/actions-reuse/issues/78>`_


1.6.1 (2022-11-29)
==================

Bugfixes
--------

- Add your info here (`#77 <https://github.com/fizyk/actions-reuse/issues/77>`_)


1.6.0 (2022-11-29)
==================

Features
--------

- Add `automerge-shared` shared workflow to re-usable workflows. (`#76 <https://github.com/fizyk/actions-reuse/issues/76>`_)


Misc
----

- `#74 <https://github.com/fizyk/actions-reuse/issues/74>`_, `#75 <https://github.com/fizyk/actions-reuse/issues/75>`_


1.5.2 (2022-11-25)
==================

Features
--------

- Removed pylint-paths parameters and now running pylint with `pylint --recursive y .` command.
  Any ignores can be set in .pylintrc file. (`#72 <https://github.com/fizyk/actions-reuse/issues/72>`_)


1.5.1 (2022-11-24)
==================

Bugfixes
--------

- Removed the ability to set up cover package's paths/names. use .coveragerc for that instead. (`#71 <https://github.com/fizyk/actions-reuse/issues/71>`_)


1.5.0 (2022-11-24)
==================

Features
--------

- Ability to set paths for linters (`#70 <https://github.com/fizyk/actions-reuse/issues/70>`_)


Misc
----

- `#68 <https://github.com/fizyk/actions-reuse/issues/68>`_, `#69 <https://github.com/fizyk/actions-reuse/issues/69>`_


1.4.1 (2022-11-18)
==================

Features
--------

- pipenv template, linters-python and tests-pytests accepts `pipenv-install-options`
  for additional pipenv install options. Might allow adding ie. `--skip-lock`. (`#67 <https://github.com/fizyk/actions-reuse/issues/67>`_)


1.4.0 (2022-11-08)
==================

Misc
----

- `#65 <https://github.com/fizyk/actions-reuse/issues/65>`_
