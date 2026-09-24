import pandas as pd

from config import CONFIG, REQUIRED_COLUMNS
from src.data_processing import load_csv_chunks, prepare_chunk
from src.analysis import CustomsAnalyzer
from src.numpy_analysis import run_numpy_comparison
from src.visualization import create_bar_plot, create_heatmap
from src.validation import (
    validate_grouped_summary,
    validate_pivot,
    validate_raw_data,
    validate_plot_values,
    create_validation_check,
    create_validation_results,
    save_validation_results,
)


def main() -> None:
    """Run the Philippine Customs data analysis."""

    output_dir = CONFIG["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer = CustomsAnalyzer(
        output_dir=output_dir,
        group_columns=CONFIG["group_columns"],
        measure_column=CONFIG["measure_column"],
    )

    chunks = load_csv_chunks(
        CONFIG["input_path"],
        REQUIRED_COLUMNS,
        CONFIG["chunksize"],
    )

    # Track the original data and excluded records.
    raw_rows = 0
    excluded_rows = 0
    raw_measure_sum = 0.0
    missing_measure_rows = 0
    invalid_measure_rows = 0

    for chunk_number, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {chunk_number}...")

        rows_before = len(chunk)

        original_values = chunk[CONFIG["measure_column"]]
        numeric_values = pd.to_numeric(
            original_values,
            errors="coerce",
        )

        raw_rows += rows_before
        raw_measure_sum += float(numeric_values.sum())

        missing_measure_rows += int(
            original_values.isna().sum()
        )

        invalid_measure_rows += int(
            (
                original_values.notna()
                & numeric_values.isna()
            ).sum()
        )

        # Count excluded records directly from the filter rules.
        excluded_mask = (
            chunk["tq"].isna()
            | numeric_values.isna()
            | (
                numeric_values
                <= CONFIG["minimum_dutiable_value_php"]
            )
        )

        excluded_rows += int(excluded_mask.sum())
        analyzer.record_operation(
            "load",
            f"Load chunk {chunk_number}",
            "Read the original CSV without modifying it",
            rows_before,
            rows_before,
        )

        analyzer.record_operation(
            "inspect",
            "Inspect numerical values",
            "Convert values to numeric for inspection; invalid values become NaN",
            rows_before,
            rows_before,
        )

        selected = prepare_chunk(
            chunk,
            CONFIG["minimum_dutiable_value_php"],
            CONFIG["high_value_threshold_million_php"],
        )

        analyzer.add_chunk(
            selected,
            rows_before,
            len(selected),
        )
        analyzer.record_operation(
            "clean",
            "Prepare selected records",
            "Convert measure to numeric; fill missing country with Missing",
            len(selected),
            len(selected),
        )

        analyzer.record_operation(
            "derive",
            "Create numerical column",
            "dutiablevalue_million_php = dutiablevaluephp / 1000000",
            len(selected),
            len(selected),
        )

        analyzer.record_operation(
            "derive",
            "Create value band",
            (
                "High when million-PHP value >= "
                f"{CONFIG['high_value_threshold_million_php']}; "
                "otherwise Standard"
            ),
            len(selected),
            len(selected),
        )

    data = analyzer.combine_chunks()

    if data.empty:
        raise SystemExit(
            "No rows matched the filter. "
            "Check the dataset and CONFIG filter values."
        )

    # Create the required summary tables.
    grouped = analyzer.create_grouped_summary(data)
    grouped_two = analyzer.create_two_category_summary(data)
    pivot = analyzer.create_pivot(grouped_two)
    top10 = analyzer.create_top10(grouped)
    summary_operations = [
        (
            "Group by country",
            "Calculate row count, valid count, sum, and mean",
            len(data),
            len(grouped),
        ),
        (
            "Group by country and tq",
            "Calculate row count and measure sum",
            len(data),
            len(grouped_two),
        ),
        (
            "Create pivot",
            "Pivot grouped sums; output row count includes Total row",
            len(grouped_two),
            len(pivot),
        ),
        (
            "Select top 10",
            "Sort country sums descending; keep up to 10 groups",
            len(grouped),
            len(top10),
        ),
    ]

    for operation, rule, before, after in summary_operations:
        analyzer.record_operation(
            "summarize",
            operation,
            rule,
            before,
            after,
        )

    # Compare the Python loop and NumPy calculation.
    numpy_results = run_numpy_comparison(data)

    numpy_results.to_csv(
        output_dir / "numpy_comparison.csv",
        index=False,
    )

    # Create plots and retain the data supplied to them.
    bar_values = create_bar_plot(
        top10,
        output_dir / "bar.png",
    )

    heatmap_values = create_heatmap(
        pivot,
        output_dir / "heatmap.png",
    )

    # Collect all validation checks.
    validation_checks = []

    validation_checks.extend(
        validate_raw_data(
            raw_rows,
            len(data),
            excluded_rows,
            raw_measure_sum,
        )
    )

    validation_checks.extend(
        validate_grouped_summary(
            data,
            grouped,
            grouped_two,
        )
    )

    validation_checks.extend(
        validate_pivot(data, pivot)
    )

    validation_checks.extend(
        validate_plot_values(
            top10,
            bar_values,
            pivot,
            heatmap_values,
        )
    )

    loop_total = float(
        numpy_results.loc[
            numpy_results["method"] == "Python loop",
            "result",
        ].iloc[0]
    )

    vector_total = float(
        numpy_results.loc[
            numpy_results["method"] == "NumPy vectorized",
            "result",
        ].iloc[0]
    )

    validation_checks.append(
        create_validation_check(
            "loop and NumPy results agree",
            loop_total,
            vector_total,
            tolerance=0.01,
        )
    )

    validation_results = create_validation_results(
        validation_checks
    )

    # Save the report and stop if any check fails.
    save_validation_results(
        validation_results,
        output_dir / "validation.csv",
    )

    # Save summary tables after validation passes.
    grouped.to_csv(
        output_dir / "grouped.csv",
        index=False,
    )

    grouped_two.to_csv(
        output_dir / "grouped_two.csv",
        index=False,
    )

    pivot.to_csv(
        output_dir / "pivot.csv",
        index=False,
    )

    top10.to_csv(
        output_dir / "top10.csv",
        index=False,
    )
    completed_outputs = [
        ("grouped.csv", len(grouped)),
        ("grouped_two.csv", len(grouped_two)),
        ("pivot.csv", len(pivot)),
        ("top10.csv", len(top10)),
        ("numpy_comparison.csv", len(numpy_results)),
        ("validation.csv", len(validation_results)),
        ("bar.png", len(bar_values)),
        ("heatmap.png", len(heatmap_values)),
    ]

    for filename, row_count in completed_outputs:
        analyzer.record_operation(
            "output",
            f"Save {filename}",
            "File saved; counts refer to table rows or plotted data rows",
            row_count,
            row_count,
        )

    analyzer.save_audit_log(
        output_dir / "audit_log.csv"
    )

    print(f"\nRaw rows: {raw_rows:,}")
    print(f"Selected rows: {len(data):,}")
    print(f"Excluded rows: {excluded_rows:,}")
    print(f"Missing numerical values: {missing_measure_rows:,}")
    print(f"Invalid numerical values: {invalid_measure_rows:,}")

    print("\nSummary tables and plots created successfully.")
    print("\nNumPy comparison:")
    print(numpy_results.to_string(index=False))


if __name__ == "__main__":
    main()
