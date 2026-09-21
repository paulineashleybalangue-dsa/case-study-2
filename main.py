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


if __name__ == "__main__":
    main()