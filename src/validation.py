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

def validate_grouped_summary(
    selected_data: pd.DataFrame,
    grouped: pd.DataFrame,
    grouped_two: pd.DataFrame,
    measure_column: str = "dutiablevaluephp",
    tolerance: float = 1,
) -> list[dict[str, object]]:
    """Validate grouped summaries against independently calculated totals."""

    selected_row_count = len(selected_data)
    selected_measure_sum = selected_data[measure_column].sum()

    grouped_row_count = grouped["row_count"].sum()
    grouped_measure_sum = grouped["measure_sum"].sum()

    grouped_two_measure_sum = grouped_two["measure_sum"].sum()

    checks = [
        create_validation_check(
            "grouped row counts",
            selected_row_count,
            grouped_row_count,
        ),
        create_validation_check(
            "grouped measure sum",
            selected_measure_sum,
            grouped_measure_sum,
            tolerance,
        ),
        create_validation_check(
            "grouped_two measure sum",
            selected_measure_sum,
            grouped_two_measure_sum,
            tolerance,
        ),
    ]

    return checks

def validate_pivot(
    selected_data: pd.DataFrame,
    pivot: pd.DataFrame,
    measure_column: str = "dutiablevaluephp",
    tolerance: float = 1,
) -> list[dict[str, object]]:
    """Validate the pivot interior total against selected data."""

    selected_measure_sum = selected_data[measure_column].sum()

    pivot_data = pivot.loc[
        pivot[pivot.columns[0]] != "Total"
    ].copy()

    value_columns = [
        column
        for column in pivot_data.columns[1:]
        if column != "Total"
    ]

    pivot_measure_sum = (
        pivot_data[value_columns]
        .sum()
        .sum()
    )

    return [
        create_validation_check(
            "pivot interior measure sum",
            selected_measure_sum,
            pivot_measure_sum,
            tolerance,
        )
    ]
