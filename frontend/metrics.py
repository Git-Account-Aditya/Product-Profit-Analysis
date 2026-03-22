import numpy as np
import pandas as pd


# ──────────────────────────────────────────────────────────────
# Product-level metrics
# ──────────────────────────────────────────────────────────────
def compute_profit_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-product profitability KPIs.

    Returned columns
    ─────────────────
    Gross Margin (%)        Gross Profit ÷ Sales × 100
    Profit per Unit         Gross Profit ÷ Units
    Cost per Unit           Cost ÷ Units
    Revenue Contribution (%)  Product Sales ÷ Total Sales × 100
    Profit Contribution (%)   Product Profit ÷ Total Profit × 100
    Margin Volatility (%)     Std-dev of monthly margin within product
    Profit (%)              Gross Profit ÷ Cost × 100
    """
    profit_df = (
        df.groupby(["Product ID", "Product Name"])[["Gross Profit", "Sales", "Units", "Cost"]]
        .sum()
        .sort_values("Gross Profit", ascending=False)
    )
    profit_df["Gross Margin (%)"] = (profit_df["Gross Profit"] / profit_df["Sales"] * 100).round(2)
    profit_df["Profit per Unit"] = (profit_df["Gross Profit"] / profit_df["Units"]).round(2)
    profit_df["Cost per Unit"] = (profit_df["Cost"] / profit_df["Units"]).round(2)
    profit_df["Revenue Contribution (%)"] = (
        profit_df["Sales"] / profit_df["Sales"].sum() * 100
    ).round(2)
    profit_df["Profit Contribution (%)"] = (
        profit_df["Gross Profit"] / profit_df["Gross Profit"].sum() * 100
    ).round(2)
    profit_df["Profit (%)"] = (profit_df["Gross Profit"] / profit_df["Cost"] * 100).round(2)

    # ── Margin Volatility (monthly std-dev of margin per product) ──
    monthly = (
        df.assign(Month=df["Order Date"].dt.to_period("M"))
        .groupby(["Product Name", "Month"])[["Sales", "Gross Profit"]]
        .sum()
    )
    monthly["Monthly Margin"] = monthly["Gross Profit"] / monthly["Sales"] * 100
    margin_vol = (
        monthly.groupby("Product Name")["Monthly Margin"]
        .std(ddof=0)
        .fillna(0)
        .round(2)
        .rename("Margin Volatility (%)")
    )
    profit_df = profit_df.reset_index().merge(margin_vol, on="Product Name", how="left")
    profit_df["Margin Volatility (%)"] = profit_df["Margin Volatility (%)"].fillna(0)

    return profit_df


# ──────────────────────────────────────────────────────────────
# Division-level metrics
# ──────────────────────────────────────────────────────────────
def compute_division_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute division-level aggregated metrics."""
    div_df = df.groupby("Division")[["Sales", "Units", "Gross Profit", "Cost"]].sum()
    div_df["Average Margin (%)"] = (div_df["Gross Profit"] / div_df["Sales"] * 100).round(2)
    div_df["Revenue Share (%)"] = (div_df["Sales"] / div_df["Sales"].sum() * 100).round(2)
    div_df["Profit Share (%)"] = (div_df["Gross Profit"] / div_df["Gross Profit"].sum() * 100).round(2)
    return div_df.reset_index()


# ──────────────────────────────────────────────────────────────
# Overall KPI summary
# ──────────────────────────────────────────────────────────────
def compute_overall_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of top-level KPIs for the filtered dataset."""
    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()
    total_cost = df["Cost"].sum()
    total_units = df["Units"].sum()
    avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    profit_per_unit = (total_profit / total_units) if total_units > 0 else 0
    num_products = df["Product Name"].nunique()

    # Margin volatility – overall monthly
    monthly = (
        df.assign(Month=df["Order Date"].dt.to_period("M"))
        .groupby("Month")[["Sales", "Gross Profit"]]
        .sum()
    )
    monthly["Margin"] = monthly["Gross Profit"] / monthly["Sales"] * 100
    overall_margin_vol = monthly["Margin"].std(ddof=0) if len(monthly) > 1 else 0.0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_cost": total_cost,
        "total_units": total_units,
        "avg_margin": avg_margin,
        "profit_per_unit": profit_per_unit,
        "num_products": num_products,
        "margin_volatility": overall_margin_vol,
    }
