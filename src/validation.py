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

def create_validation_results(
    checks: list[dict[str, object]],
) -> pd.DataFrame:
    """Create a validation results table from individual checks."""

    return pd.DataFrame(
        checks,
        columns=[
            "check",
            "expected",
            "actual",
            "tolerance",
            "pass",
        ],
    )

def save_validation_results(
    results: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save validation results and stop if any check fails."""

    results.to_csv(output_path, index=False)

    failed = results.loc[~results["pass"]]

    if not failed.empty:
        print("VALIDATION FAILED")
        print(failed.to_string(index=False))
        raise SystemExit(1)

    print("All validation checks passed.")

def validate_selected_data(
    data: pd.DataFrame,
    expected_rows: int,
    expected_measure_sum: float,
    measure_column: str = "dutiablevaluephp",
    tolerance: float = 1,
) -> list[dict[str, object]]:
    
    """Validate the selected row count and measure sum."""

    actual_rows = len(data)
    actual_measure_sum = data[measure_column].sum()

    checks = [
        create_validation_check(
            "selected row count",
            expected_rows,
            actual_rows,
        ),
        create_validation_check(
            "selected measure sum",
            expected_measure_sum,
            actual_measure_sum,
            tolerance,
        ),
    ]

    return checks



