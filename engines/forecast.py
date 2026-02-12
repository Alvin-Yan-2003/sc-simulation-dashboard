import numpy as np

def exponential_smoothing(demand_series, alpha=0.3):
    forecast = [demand_series[0]]

    for t in range(1, len(demand_series)):
        f = alpha * demand_series[t-1] + (1 - alpha) * forecast[-1]
        forecast.append(f)

    return np.array(forecast)