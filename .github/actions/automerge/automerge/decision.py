"""The verdict every rule returns."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class Decision:
    """Whether to arm a pull request, and why, phrased to follow ``Pull request #N``."""

    arm: bool
    reason: str
