from dataclasses import dataclass


@dataclass
class CostConfig:
    holding_cost: float = 1.0
    order_cost: float = 100.0
    penalty_cost: float = 5.0


@dataclass
class Thresholds:
    dio_slow_moving_days: int = 60
    capacity_warning_pct: float = 85
    capacity_critical_pct: float = 100
    service_level_target: float = 0.95


@dataclass
class SimulationConfig:
    weeks: int = 52
    base_level: int = 5000
    use_forecast: bool = True
    alpha: float = 0.3

    policy: str = "EOQ"
    lead_time: int = 2
    eoq_qty: int = 5000
    s: int = 3000
    S: int = 8000

    capacity: int = 20000
