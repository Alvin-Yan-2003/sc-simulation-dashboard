import numpy as np
import pandas as pd

def simulate_inventory(
    demand,
    policy="EOQ",
    lead_time=2,
    order_cost=100,
    holding_cost=1,
    eoq_qty=5000,
    s=3000,
    S=8000,
    initial_stock=10000
):

    weeks = len(demand)
    stock = initial_stock
    pipeline = [0] * lead_time

    records = []

    for t in range(weeks):

        receipt = pipeline.pop(0)
        stock += receipt

        d = demand[t]
        fulfilled = min(stock, d)
        lost_sales = max(d - stock, 0)

        stock -= fulfilled

        order_qty = 0

        if policy == "EOQ":
            if stock < eoq_qty:
                order_qty = eoq_qty

        elif policy == "(s,S)":
            if stock < s:
                order_qty = S - stock

        pipeline.append(order_qty)

        records.append({
            "Week": t+1,
            "Demand": d,
            "Stock": stock,
            "Order": order_qty,
            "Lost_Sales": lost_sales,
            "Fulfilled": fulfilled
        })

    return pd.DataFrame(records)