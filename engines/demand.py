import numpy as np
import pandas as pd

def generate_demand(
    weeks=52,
    base_level=5000,
    trend_growth=0.002,
    seasonality_strength=0.15,
    noise_std=300,
    seed=42
):
    rng = np.random.default_rng(seed)
    t = np.arange(weeks)

    trend = base_level * (1 + trend_growth) ** t
    seasonality = 1 + seasonality_strength * np.sin(2 * np.pi * t / 12)
    noise = rng.normal(0, noise_std, size=weeks)

    demand = trend * seasonality + noise

    df = pd.DataFrame({
        "Week": np.arange(1, weeks + 1),
        "Actual_Demand": np.maximum(demand, 0).round(0)
    })

    return df