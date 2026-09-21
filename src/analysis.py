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

    def add_chunk(
        self,
        chunk: pd.DataFrame,
        rows_before: int,
        rows_after: int,
    ) -> None:
        """Store a processed chunk and record its audit information."""
        self.processed_chunks.append(chunk)

        self.audit_records.append(
            {
                "step": f"chunk_{len(self.processed_chunks)}",
                "operation": "filter_and_prepare",
                "rule": "tq not missing and dutiablevaluephp > minimum",
                "rows_before": rows_before,
                "rows_after": rows_after,
            }
        )

    def combine_chunks(self) -> pd.DataFrame:
        """Combine all processed chunks into one DataFrame."""
        if not self.processed_chunks:
            return pd.DataFrame()

        return pd.concat(
            self.processed_chunks,
            ignore_index=True,
        )

    def create_grouped_summary(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create a grouped summary using counts and total value."""
        grouped = (
            data.groupby(
                self.group_columns,
                dropna=False,
            )[self.measure_column]
            .agg(
                record_count="count",
                total_value_php="sum",
            )
            .reset_index()
        )

        return grouped

    def create_two_category_summary(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create a summary using the two configured grouping columns."""
        grouped = (
            data.groupby(
                self.group_columns,
                dropna=False,
            )[self.measure_column]
            .agg(
                record_count="count",
                total_value_php="sum",
            )
            .reset_index()
        )

        return grouped