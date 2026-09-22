from config import CONFIG, REQUIRED_COLUMNS
from src.data_processing import load_csv_chunks, prepare_chunk
from src.analysis import CustomsAnalyzer
from src.numpy_analysis import run_numpy_comparison
from src.visualization import create_bar_plot, create_heatmap
from src.validation import (
    validate_grouped_summary,
    validate_pivot,
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

    chunk_number = 0

    for chunk in chunks:
        chunk_number += 1
        print(f"Processing chunk {chunk_number}...")

        rows_before = len(chunk)

        selected = prepare_chunk(
            chunk,
            CONFIG["minimum_dutiable_value_php"],
            CONFIG["high_value_threshold_million_php"],
        )

        rows_after = len(selected)

        analyzer.add_chunk(
            selected,
            rows_before,
            rows_after,
        )

    data = analyzer.combine_chunks()

    grouped = analyzer.create_grouped_summary(data)
    grouped_two = analyzer.create_two_category_summary(data)
    pivot = analyzer.create_pivot(grouped_two)
    top10 = analyzer.create_top10(grouped)

    numpy_results = run_numpy_comparison(data)

    numpy_results.to_csv(
        output_dir / "numpy_comparison.csv",
        index=False,
    )

    # Validation
    validation_checks = []

    validation_checks.extend(
        validate_grouped_summary(
            data,
            grouped,
            grouped_two,
        )
    )

    validation_checks.extend(
        validate_pivot(
            data,
            pivot,
        )
    )

    validation_results = create_validation_results(
        validation_checks
    )

    save_validation_results(
        validation_results,
        output_dir / "validation.csv",
    )

    create_bar_plot(
        top10,
        output_dir / "bar.png",
    )

    create_heatmap(
        pivot,
        output_dir / "heatmap.png",
    )

    # Save summary tables
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

    # Save audit log
    analyzer.save_audit_log(
        output_dir / "audit_log.csv"
    )

    print()
    print("Summary tables created successfully.")

    print()
    print("NumPy comparison:")
    print(numpy_results.to_string(index=False))


if __name__ == "__main__":
    main()