from pathlib import Path

import pandas as pd

class CustomsAnalyzer:
    """Analyze processed Philippine Customs data."""

    def __init__(
        self,
        output_dir: Path,
        group_columns: list[str],
        measure_column: str,
    ) -> None:
        self.output_dir = output_dir
        self.group_columns = group_columns
        self.measure_column = measure_column
        self.processed_chunks: list[pd.DataFrame] = []
        self.audit_records: list[dict[str, object]] = []