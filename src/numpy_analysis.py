import time

import numpy as np
import pandas as pd

def calculate_loop(values: np.ndarray) -> float:
    """Calculate the total using a Python loop."""

    total = 0.0

    for value in values:
        total += value * 1.10

    return total

def calculate_vectorized(values: np.ndarray) -> float:
    """Calculate the total using NumPy vectorization."""

    return np.sum(values * 1.10)

def run_numpy_comparison(
    data: pd.DataFrame,
    sample_size: int = 10_000,
    runs: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    """Compare loop and vectorized NumPy calculations."""

    values = data["dutiablevaluephp"].to_numpy(dtype=float)

    rng = np.random.default_rng(seed)

    sample_indices = rng.choice(
        len(values),
        size=min(sample_size, len(values)),
        replace=False,
    )

    sample = values[sample_indices]

    positive_mask = sample > 0
    sample = sample[positive_mask]