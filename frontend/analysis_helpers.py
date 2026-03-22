import numpy as np
import pandas as pd

def compute_product_pareto(df: pd.DataFrame) -> dict:
    """Compute product-level Pareto data for revenue and profit."""
    product_df = (
        df.groupby('Product Name')[['Sales', 'Gross Profit']].sum()
        .sort_values('Sales', ascending=False)
    )
    total_products = len(product_df)

    # Revenue pareto
    product_df['Revenue Share (%)'] = product_df['Sales'] / product_df['Sales'].sum() * 100
    product_df['Cumulative Revenue (%)'] = product_df['Revenue Share (%)'].cumsum()
    products_80_rev = (product_df[product_df['Cumulative Revenue (%)'] <= 80].shape[0] + 1)

    # Profit pareto
    profit_sorted = product_df.sort_values('Gross Profit', ascending=False).copy()
    profit_sorted['Profit Share (%)'] = profit_sorted['Gross Profit'] / profit_sorted['Gross Profit'].sum() * 100
    profit_sorted['Cumulative Profit (%)'] = profit_sorted['Profit Share (%)'].cumsum()
    products_80_profit = (profit_sorted[profit_sorted['Cumulative Profit (%)'] <= 80].shape[0] + 1)

    return {
        'revenue_df': product_df.reset_index(),
        'profit_df': profit_sorted.reset_index(),
        'total_products': total_products,
        'products_80_rev': products_80_rev,
        'products_80_profit': products_80_profit,
        'pct_80_rev': products_80_rev / total_products * 100,
        'pct_80_profit': products_80_profit / total_products * 100,
    }


def compute_state_congestion(df: pd.DataFrame) -> dict:
    """Compute state/region congestion risk data."""
    region_df = (
        df.groupby('Region').agg(
            Total_Orders=('Order ID', 'nunique'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Gross Profit', 'sum'),
            Unique_States=('State/Province', 'nunique'),
        ).sort_values('Total_Orders', ascending=False)
    )
    region_df['Order Share (%)'] = region_df['Total_Orders'] / region_df['Total_Orders'].sum() * 100
    region_df['Revenue Share (%)'] = region_df['Total_Sales'] / region_df['Total_Sales'].sum() * 100
    region_df['Orders per State'] = (region_df['Total_Orders'] / region_df['Unique_States']).round(1)

    state_df = (
        df.groupby(['State/Province', 'Region']).agg(
            Total_Orders=('Order ID', 'nunique'),
            Total_Sales=('Sales', 'sum'),
        ).sort_values('Total_Orders', ascending=False)
    )
    state_df['Order Share (%)'] = state_df['Total_Orders'] / state_df['Total_Orders'].sum() * 100
    state_df['Cumulative Order Share (%)'] = state_df['Order Share (%)'].cumsum()
    state_df['Revenue Share (%)'] = state_df['Total_Sales'] / state_df['Total_Sales'].sum() * 100

    def risk_label(share):
        if share >= 5: return 'HIGH'
        elif share >= 2: return 'MEDIUM'
        return 'LOW'

    state_df['Risk'] = state_df['Order Share (%)'].apply(risk_label)
    states_80 = state_df[state_df['Cumulative Order Share (%)'] <= 80].shape[0] + 1

    # HHI
    region_hhi = (region_df['Revenue Share (%)'] ** 2).sum()

    return {
        'region_df': region_df.reset_index(),
        'state_df': state_df.reset_index(),
        'states_80': states_80,
        'total_states': len(state_df),
        'region_hhi': region_hhi,
    }


def compute_cost_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute product-level cost structure and action flags."""
    prod = (
        df.groupby('Product Name').agg(
            Total_Sales=('Sales', 'sum'),
            Total_Cost=('Cost', 'sum'),
            Total_Profit=('Gross Profit', 'sum'),
            Total_Units=('Units', 'sum'),
        ).sort_values('Total_Sales', ascending=False)
    )
    prod['Margin (%)'] = prod['Total_Profit'] / prod['Total_Sales'] * 100
    prod['Cost Ratio (%)'] = prod['Total_Cost'] / prod['Total_Sales'] * 100
    prod['Avg Price/Unit'] = prod['Total_Sales'] / prod['Total_Units']
    prod['Avg Cost/Unit'] = prod['Total_Cost'] / prod['Total_Units']
    prod['Markup (%)'] = (prod['Avg Price/Unit'] - prod['Avg Cost/Unit']) / prod['Avg Cost/Unit'] * 100
    prod['Profit/Unit'] = prod['Total_Profit'] / prod['Total_Units']
    prod['Revenue Share (%)'] = prod['Total_Sales'] / prod['Total_Sales'].sum() * 100
    prod['Profit Share (%)'] = prod['Total_Profit'] / prod['Total_Profit'].sum() * 100
    prod['Profit-Revenue Gap'] = prod['Profit Share (%)'] - prod['Revenue Share (%)']

    overall_margin = prod['Total_Profit'].sum() / prod['Total_Sales'].sum() * 100
    median_markup = prod['Markup (%)'].median()

    def flag(row):
        flags = []
        if row['Margin (%)'] < 15 and row['Revenue Share (%)'] < 1:
            flags.append('Discontinuation Review')
        if row['Cost Ratio (%)'] > 50 and row['Margin (%)'] < overall_margin:
            flags.append('Cost Renegotiation')
        need_reprice = (
            (row['Margin (%)'] < overall_margin and row['Revenue Share (%)'] > 0.5)
            or row['Profit-Revenue Gap'] < -0.5
            or (row['Markup (%)'] < median_markup and row['Margin (%)'] < overall_margin)
        )
        if need_reprice:
            flags.append('Repricing')
        if not flags:
            flags.append('No Action Needed')
        return ', '.join(flags)

    prod['Action'] = prod.apply(flag, axis=1)
    prod['Primary Action'] = prod['Action'].apply(lambda x: x.split(',')[0].strip())
    return prod.reset_index(), overall_margin
