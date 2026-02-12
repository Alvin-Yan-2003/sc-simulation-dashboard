from engines.demand import generate_demand
from engines.forecast import exponential_smoothing
from engines.inventory import simulate_inventory
from engines.warehouse import apply_capacity
from engines.kpi import compute_kpis

import inspect
import engines.kpi

print("KPI FILE:", engines.kpi.__file__)
print("SIGNATURE:", inspect.signature(engines.kpi.compute_kpis))


def run_simulation(sim_config, cost_config):

    df_demand = generate_demand(
        weeks=sim_config.weeks,
        base_level=sim_config.base_level
    )

    # Forecast layer
    if sim_config.use_forecast:
        forecast = exponential_smoothing(
            df_demand["Actual_Demand"].values,
            alpha=sim_config.alpha
        )
        demand_input = forecast
        df_demand["Forecast"] = forecast
    else:
        demand_input = df_demand["Actual_Demand"].values

    # Inventory layer
    df_inventory = simulate_inventory(
        demand=demand_input,
        policy=sim_config.policy,
        lead_time=sim_config.lead_time,
        eoq_qty=sim_config.eoq_qty,
        s=sim_config.s,
        S=sim_config.S
    )

    # Warehouse constraint
    df_inventory = apply_capacity(
        df_inventory,
        sim_config.capacity
    )

    # KPI layer
    kpis = compute_kpis(
        df_inventory,
        holding_cost=cost_config.holding_cost,
        order_cost=cost_config.order_cost,
        penalty_cost=cost_config.penalty_cost
    )

    return df_demand, df_inventory, kpis