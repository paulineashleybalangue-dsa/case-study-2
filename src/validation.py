from pathlib import Path

import pandas as pd


def create_validation_check(
    check: str,
    expected: object,
    actual: object,
    tolerance: float = 0,
) -> dict[str, object]:
    """Create one validation check record."""

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        passed = abs(actual - expected) <= tolerance
    else:
        passed = actual == expected

    return {
        "check": check,
        "expected": expected,
        "actual": actual,
        "tolerance": tolerance,
        "pass": passed,
    }
