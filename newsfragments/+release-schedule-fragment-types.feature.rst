Make ``shared-release-schedule`` bump levels configurable through ``minor-fragments`` and ``major-fragments``, both taking their previous behaviour as defaults.
Previously only ``feature`` raised the minor and nothing raised the major, so a ``break`` fragment released as a patch. On a pre-1.0 project list the breaking type under ``minor-fragments`` and leave ``major-fragments`` empty.
