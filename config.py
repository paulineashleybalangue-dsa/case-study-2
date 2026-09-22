from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    "input_path": BASE_DIR / "data" / "Philippine Customs BetterGov.PH 2015.csv",
    "output_dir": BASE_DIR / "output",
    "chunksize": 100_000,
    "minimum_dutiable_value_php": 0,
    "high_value_threshold_million_php": 100,
    "group_columns": ["countryorigin_iso3", "tq"],
    "measure_column": "dutiablevaluephp",
}

REQUIRED_COLUMNS = {
    "countryorigin_iso3",
    "tq",
    "dutiablevaluephp",
}