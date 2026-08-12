Support triggering ``shared-automerge`` on ``pull_request_target``, which is now the preferred trigger.
Arming auto-merge is a one-shot action, so the ``workflow_run``/``check_suite`` triggers ran the job once per finished check to do work only needed once; they remain supported.
``pull_request`` is not supported, since dependabot-triggered ``pull_request`` runs get no repository secrets and cannot mint the app token.
