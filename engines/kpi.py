def compute_kpis(df, holding_cost=1, order_cost=0, penalty_cost=0):

    total_demand = df["Demand"].sum()
    total_fulfilled = df["Fulfilled"].sum()
    total_lost = df["Lost_Sales"].sum()

    fill_rate = total_fulfilled / total_demand if total_demand > 0 else 0
    service_level = 1 - (df["Lost_Sales"] > 0).mean()

    avg_inventory = df["Stock"].mean()
    weekly_demand = total_demand / len(df) if len(df) > 0 else 0
    dio = (avg_inventory / weekly_demand) * 7 if weekly_demand > 0 else 0

    # Cost calculation
    holding_total = avg_inventory * holding_cost
    total_orders = df["Order_Placed"].sum() if "Order_Placed" in df.columns else 0
    ordering_total = total_orders * order_cost
    penalty_total = total_lost * penalty_cost

    total_cost = holding_total + ordering_total + penalty_total

    return {
        "Fill Rate": round(fill_rate, 3),
        "Service Level": round(service_level, 3),
        "DIO": round(dio, 1),
        "Avg Inventory": round(avg_inventory, 0),
        "Holding Cost": round(holding_total, 0),
        "Ordering Cost": round(ordering_total, 0),
        "Penalty Cost": round(penalty_total, 0),
        "Total Cost": round(total_cost, 0)
    }