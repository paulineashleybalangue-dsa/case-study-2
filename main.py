from config import CONFIG, REQUIRED_COLUMNS
from src.data_processing import load_csv_chunks, prepare_chunk
from src.analysis import CustomsAnalyzer

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


if __name__ == "__main__":
    main()