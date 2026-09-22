from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def create_bar_plot(
    top10: pd.DataFrame,
    output_path: Path,
) -> None:
    """Create a bar chart showing the top groups by total dutiable value."""

    plot_data = top10.sort_values(
        "measure_sum",
        ascending=True,
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        plot_data["countryorigin_iso3"],
        plot_data["measure_sum"],
    )

    plt.title(
        "Top 10 Countries by Total Dutiable Value"
    )

    plt.xlabel(
        "Total Dutiable Value (PHP)"
    )

    plt.ylabel(
        "Country of Origin"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()