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