from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


Period = Literal["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26"]


PERIODS: list[Period] = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26"]
INV_TYPES = ["All", "Finished goods (factory)", "Finished goods (3PL)", "Raw sugar"]
BUs = ["All BUs", "TTCS-B2B", "NHS", "Kho B2B", "TTCGL", "ATN", "KSK raw", "Kho B2C"]


@dataclass(frozen=True)
class Thresholds:
    heatmap_green_lt: float = 0.80
    heatmap_yellow_lt: float = 1.00
    dio_slow_moving_days: int = 60


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def make_locations() -> list[str]:
    return [
        "Kho B2B - HCM",
        "Kho B2B - HN",
        "NHS - Tay Ninh",
        "TTCS-B2B - Gia Lai",
        "TTCGL - HCM",
        "ATN - HN",
        "Kho B2C - HCM",
        "Kho B2C - HN",
    ]


def make_overview_kpis(seed: int = 42) -> dict[str, float]:
    r = _rng(seed)
    total_ending_stock_t = float(r.normal(185_000, 8_000))
    cap_util_avg = float(np.clip(r.normal(0.88, 0.06), 0.55, 1.25))
    over_capacity_count = int(max(0, round(r.normal(2.2, 1.2))))
    total_overflow_t = float(max(0, r.normal(7_500, 3_500)))
    est_cost_bvnd = float(max(0, r.normal(42.5, 6.0)))
    dio_avg = float(np.clip(r.normal(58, 9), 25, 110))
    return {
        "Total Ending Stock (tons)": round(total_ending_stock_t, 0),
        "Capacity Util. (Avg)": round(cap_util_avg * 100, 1),
        "# Over Capacity": float(over_capacity_count),
        "Total Overflow (tons)": round(total_overflow_t, 0),
        "Est. Cost (WH+Trans) (B VND)": round(est_cost_bvnd, 1),
        "DIO (Avg) (days)": round(dio_avg, 0),
    }


def make_usage_heatmap(periods: list[Period] = PERIODS, seed: int = 42) -> pd.DataFrame:
    r = _rng(seed)
    locs = make_locations()
    base = r.normal(0.86, 0.08, size=(len(locs), len(periods)))
    spikes = r.choice([0.0, 0.12, 0.22], p=[0.75, 0.20, 0.05], size=base.shape)
    usage = np.clip(base + spikes, 0.50, 1.35)
    df = pd.DataFrame(usage, index=locs, columns=periods)
    return (df * 100).round(1)


def make_stock_capacity(period: Period = "Jan-26", seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 7)
    locs = make_locations()
    capacity = r.integers(12_000, 36_000, size=len(locs)).astype(float)
    ending = (capacity * r.normal(0.92, 0.12, size=len(locs))).clip(5_000, 45_000)
    df = pd.DataFrame(
        {
            "Location": locs,
            "Capacity (tons)": capacity.round(0),
            "Ending Stock (tons)": ending.round(0),
        }
    )
    df["Usage %"] = (df["Ending Stock (tons)"] / df["Capacity (tons)"] * 100).round(1)
    return df.sort_values("Ending Stock (tons)", ascending=False).reset_index(drop=True)


def make_cost_breakdown(periods: list[Period] = PERIODS, seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 99)
    rent = r.normal(8.5, 1.1, size=len(periods)).clip(5, 13)
    transport = r.normal(24.0, 3.0, size=len(periods)).clip(16, 34)
    handling = r.normal(9.2, 1.6, size=len(periods)).clip(5, 15)
    return pd.DataFrame(
        {
            "Period": periods,
            "Warehouse Rent (B VND)": np.round(rent, 1),
            "Transport (B VND)": np.round(transport, 1),
            "Handling (B VND)": np.round(handling, 1),
        }
    )


def make_alerts(seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 123)
    locs = make_locations()
    issues = ["Over capacity", "Slow-moving", "Shortage risk", "High DIO", "High-cost lane"]
    owners = ["LOGS", "Planning", "ComC", "Finance"]
    sev = ["High", "Medium", "Low"]

    rows = []
    for _ in range(18):
        issue = r.choice(issues, p=[0.28, 0.22, 0.18, 0.20, 0.12])
        severity = r.choice(sev, p=[0.35, 0.45, 0.20])
        est_cost = float(max(0, r.normal(1.6 if severity == "High" else 0.7, 0.5)))
        rec = {
            "Over capacity": "Transfer to 3PL / rebalance to low-usage sites",
            "Slow-moving": "Push sales / promo / review demand plan",
            "Shortage risk": "Increase KHSX / prioritize replenishment",
            "High DIO": "Reduce inbound / accelerate outbound",
            "High-cost lane": "Renegotiate contract / consolidate loads",
        }[issue]
        rows.append(
            {
                "Location": r.choice(locs),
                "Issue": issue,
                "Severity": severity,
                "Est. Cost (B VND)": round(est_cost, 2),
                "Recommendation": rec,
                "Owner": r.choice(owners),
            }
        )
    df = pd.DataFrame(rows).sort_values(["Severity", "Est. Cost (B VND)"], ascending=[True, False])
    return df.reset_index(drop=True)


def make_inventory_table(seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 555)
    inv_orgs = ["129501", "129502", "129503", "129504"]
    wh_by_bu = {
        "TTCS-B2B": ["TTCS-B2B - Gia Lai"],
        "NHS": ["NHS - Tay Ninh"],
        "Kho B2B": ["Kho B2B - HCM", "Kho B2B - HN"],
        "TTCGL": ["TTCGL - HCM"],
        "ATN": ["ATN - HN"],
        "KSK raw": ["KSK raw - Tay Ninh"],
        "Kho B2C": ["Kho B2C - HCM", "Kho B2C - HN"],
    }
    types = ["Thành phẩm NM", "Thành phẩm kho thuê", "Raw sugar"]

    rows = []
    for period in PERIODS:
        for bu, whs in wh_by_bu.items():
            for wh in whs:
                inv_org = r.choice(inv_orgs)
                typ = r.choice(types, p=[0.46, 0.34, 0.20])
                opening = float(max(0, r.normal(18_000, 6_500)))
                inbound = float(max(0, r.normal(9_500, 4_000)))
                outbound = float(max(0, r.normal(10_200, 4_400)))
                ending = max(0.0, opening + inbound - outbound)
                capacity = float(r.integers(14_000, 34_000))
                usage = ending / capacity if capacity else 0.0
                overflow = max(0.0, ending - capacity)
                cost_bvnd = float(max(0, (ending / 10_000) * r.normal(0.6, 0.12)))
                rows.append(
                    {
                        "Period": period,
                        "INV ORG": inv_org,
                        "BU / Warehouse": f"{bu} / {wh}",
                        "Type": typ,
                        "Opening": round(opening, 0),
                        "Inbound": round(inbound, 0),
                        "Outbound": round(outbound, 0),
                        "Ending": round(ending, 0),
                        "Capacity": round(capacity, 0),
                        "Usage %": round(usage * 100, 1),
                        "Overflow": round(overflow, 0),
                        "Cost (B VND)": round(cost_bvnd, 2),
                    }
                )
    return pd.DataFrame(rows)


def make_transport_lane_table(seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 808)
    bus = ["TTCS-B2B", "NHS", "Kho B2B", "TTCGL", "ATN"]
    lanes = [
        "Factory → Kho B2B",
        "Factory → Trade",
        "Factory → SME",
        "Tràn → Kho B2B",
        "Tràn → 3PL",
        "Kho B2B → B2C",
    ]
    rows = []
    for period in PERIODS:
        for _ in range(16):
            bu = r.choice(bus)
            lane = r.choice(lanes, p=[0.22, 0.18, 0.14, 0.18, 0.12, 0.16])
            vol = float(max(0, r.normal(5_200, 2_300)))
            trans = float(max(0, (vol / 1_000) * r.normal(2.4, 0.5)))
            handling = float(max(0, (vol / 1_000) * r.normal(0.85, 0.18)))
            rent = float(max(0, r.normal(0.65, 0.15)))
            note = "Overflow transfer" if "Tràn" in lane else "Normal"
            rows.append(
                {
                    "Period": period,
                    "BU": bu,
                    "Lane": lane,
                    "Volume (Tons)": round(vol, 0),
                    "Transport Cost (B VND)": round(trans, 2),
                    "Handling Cost (B VND)": round(handling, 2),
                    "Warehouse Rent (B VND)": round(rent, 2),
                    "Notes": note,
                }
            )
    return pd.DataFrame(rows)


def make_simulation_weekly(seed: int = 42) -> pd.DataFrame:
    r = _rng(seed + 9001)
    weeks = [f"W{i}" for i in range(1, 9)]
    baseline = np.maximum(0, r.normal(180_000, 9_000, size=len(weeks)))
    df = pd.DataFrame({"Week": weeks, "Baseline": np.round(baseline, 0)})
    return df


def simulate_demand(df_weekly: pd.DataFrame, scenario: str) -> pd.DataFrame:
    multipliers = {
        "Demand 1": 1.00,
        "Demand 2": 1.06,
        "Demand 3": 0.95,
        "Demand 4": 1.12,
    }
    m = multipliers.get(scenario, 1.0)
    out = df_weekly.copy()
    out["Simulated"] = np.round(out["Baseline"] * m, 0)
    return out


def scenario_summary(simulated_peak_usage_pct: float, overflow_tons: float, cost_bvnd: float) -> dict[str, str]:
    if simulated_peak_usage_pct >= 110:
        risk = "Critical"
    elif simulated_peak_usage_pct >= 103:
        risk = "Cao"
    elif simulated_peak_usage_pct >= 95:
        risk = "High"
    else:
        risk = "Low"
    return {
        "Peak Usage %": f"{simulated_peak_usage_pct:.1f}%",
        "Overflow Risk": risk,
        "Cost Estimate": f"{cost_bvnd:,.1f} B VND",
        "Overflow (tons)": f"{overflow_tons:,.0f}",
    }

def make_sku_master(n_sku: int = 50, seed: int = 42):
    r = _rng(seed + 1000)
    skus = []
    for i in range(n_sku):
        skus.append({
            "SKU": f"SKU-{1000+i}",
            "BU": r.choice(BUs[1:]),
            "Unit cost": round(r.normal(12, 3), 2),
            "Lead time (weeks)": r.integers(1, 4),
            "Safety stock": r.integers(200, 800),
            "Reorder point": r.integers(1500, 3000),
            "Max level": r.integers(4000, 8000),
            "Order cost": round(r.normal(5, 1), 2),
            "Holding cost %": round(r.uniform(0.15, 0.30), 2),
        })
    return pd.DataFrame(skus)

def make_weekly_demand(n_sku=50, weeks=8, seed=42):
    r = _rng(seed + 2000)
    locations = make_locations()
    data = []

    for sku in range(n_sku):
        for loc in locations:
            for w in range(1, weeks+1):
                demand = max(0, r.normal(800, 250))
                data.append({
                    "SKU": f"SKU-{1000+sku}",
                    "Location": loc,
                    "Week": f"W{w}",
                    "Demand": round(demand, 0)
                })

    return pd.DataFrame(data)

def make_opening_inventory(n_sku=50, seed=42):
    r = _rng(seed + 3000)
    locations = make_locations()
    data = []

    for sku in range(n_sku):
        for loc in locations:
            opening = max(0, r.normal(5000, 1500))
            data.append({
                "SKU": f"SKU-{1000+sku}",
                "Location": loc,
                "Opening": round(opening, 0)
            })

    return pd.DataFrame(data)
