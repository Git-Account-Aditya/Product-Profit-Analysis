import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from analysis_helpers import compute_product_pareto, compute_state_congestion, compute_cost_diagnostics

# ──────────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Profit Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Custom CSS for premium dark theme
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25);
    }
    div[data-testid="stMetric"] label {
        color: #a0a0b8 !important;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.75rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e0e0ff !important;
        font-weight: 700;
        font-size: 1.8rem !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #13131f 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(139, 92, 246, 0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #c4b5fd !important;
    }

    /* Headers */
    h1 {
        background: linear-gradient(90deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #c4b5fd !important;
        font-weight: 600 !important;
    }

    /* Divider */
    hr {
        border-color: rgba(139, 92, 246, 0.2) !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 24px;
        font-weight: 500;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parent.parent / "datasets" / "cleaned_dataset.csv"
    df = pd.read_csv(data_path)
    return df


def compute_profit_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-product profitability metrics."""
    profit_df = (
        df.groupby(["Product ID", "Product Name"])[["Gross Profit", "Sales", "Units", "Cost"]]
        .sum()
        .sort_values("Gross Profit", ascending=False)
    )
    profit_df["Gross Margin (%)"] = (profit_df["Gross Profit"] / profit_df["Sales"] * 100).round(2)
    profit_df["Profit per Unit"] = (profit_df["Gross Profit"] / profit_df["Units"]).round(2)
    profit_df["Cost per Unit"] = (profit_df["Cost"] / profit_df["Units"]).round(2)
    profit_df["Profit Contribution (%)"] = (
        profit_df["Gross Profit"] / profit_df["Gross Profit"].sum() * 100
    ).round(2)
    profit_df["Profit (%)"] = (profit_df["Gross Profit"] / profit_df["Cost"] * 100).round(2)
    return profit_df.reset_index()


def compute_division_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute division-level aggregated metrics."""
    div_df = df.groupby("Division")[["Sales", "Units", "Gross Profit", "Cost"]].sum()
    div_df["Average Margin (%)"] = (div_df["Gross Profit"] / div_df["Sales"] * 100).round(2)
    div_df["Revenue Share (%)"] = (div_df["Sales"] / div_df["Sales"].sum() * 100).round(2)
    div_df["Profit Share (%)"] = (div_df["Gross Profit"] / div_df["Gross Profit"].sum() * 100).round(2)
    return div_df.reset_index()


def compute_region_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute region-level aggregated metrics."""
    reg_df = df.groupby("Region")[["Sales", "Units", "Gross Profit", "Cost"]].sum()
    reg_df["Average Margin (%)"] = (reg_df["Gross Profit"] / reg_df["Sales"] * 100).round(2)
    reg_df["Revenue Share (%)"] = (reg_df["Sales"] / reg_df["Sales"].sum() * 100).round(2)
    reg_df["Profit Share (%)"] = (reg_df["Gross Profit"] / reg_df["Gross Profit"].sum() * 100).round(2)
    return reg_df.reset_index()


# ──────────────────────────────────────────────────────────────
# Color palette
# ──────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#8b5cf6",
    "secondary": "#06b6d4",
    "accent": "#f472b6",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#f87171",
}

CHART_COLORS = [
    "#8b5cf6", "#06b6d4", "#f472b6", "#34d399", "#fbbf24",
    "#f87171", "#a78bfa", "#22d3ee", "#fb923c", "#4ade80",
    "#e879f9", "#38bdf8", "#facc15", "#fb7185", "#2dd4bf",
]

PLOTLY_TEMPLATE = "plotly_dark"


# ──────────────────────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────────────────────
def main():
    df = load_data()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("## 🍫 Filters")
        st.markdown("---")

        # Division filter
        all_divisions = sorted(df["Division"].unique())
        selected_divisions = st.multiselect(
            "Division",
            options=all_divisions,
            default=all_divisions,
            key="div_filter",
        )

        # Region filter
        all_regions = sorted(df["Region"].unique())
        selected_regions = st.multiselect(
            "Region",
            options=all_regions,
            default=all_regions,
            key="reg_filter",
        )

        # Ship Mode filter
        all_ship_modes = sorted(df["Ship Mode"].unique())
        selected_ship_modes = st.multiselect(
            "Ship Mode",
            options=all_ship_modes,
            default=all_ship_modes,
            key="ship_filter",
        )

        st.markdown("---")
        st.markdown(
            "<p style='color:#6b6b8d;font-size:0.75rem;text-align:center;'>"
            "Nassau Candy Distributor<br>Product Profit Analysis</p>",
            unsafe_allow_html=True,
        )

    # Apply filters
    filtered_df = df[
        (df["Division"].isin(selected_divisions))
        & (df["Region"].isin(selected_regions))
        & (df["Ship Mode"].isin(selected_ship_modes))
    ]

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your filters.")
        return

    # ── Header ──
    st.markdown("# 📊 Product Profit Analyzer")
    st.markdown(
        "<p style='color:#8888aa;margin-top:-12px;margin-bottom:24px;font-size:1.05rem;'>"
        "Nassau Candy Distributor — Interactive Profitability Dashboard</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Row ──
    total_sales = filtered_df["Sales"].sum()
    total_profit = filtered_df["Gross Profit"].sum()
    total_cost = filtered_df["Cost"].sum()
    total_units = filtered_df["Units"].sum()
    avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Sales", f"${total_sales:,.2f}")
    k2.metric("Gross Profit", f"${total_profit:,.2f}")
    k3.metric("Total Cost", f"${total_cost:,.2f}")
    k4.metric("Units Sold", f"{total_units:,}")
    k5.metric("Avg. Margin", f"{avg_margin:.1f}%")

    st.markdown("---")

    # ── Tabs ──
    tab_overview, tab_products, tab_divisions, tab_pareto, tab_geo, tab_cost, tab_data = st.tabs(
        ["📈 Overview", "🏷️ Products", "🏢 Division", "📊 Pareto", "🗺️ Geographic Risk", "💰 Cost Diagnostics", "📋 Data"]
    )

    # ──────────────────────────────────────────────────────────
    # TAB 1 — Overview
    # ──────────────────────────────────────────────────────────
    with tab_overview:
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("### Sales vs Profit by Division")
            div_agg = filtered_df.groupby("Division")[["Sales", "Gross Profit"]].sum().reset_index()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=div_agg["Division"], y=div_agg["Sales"],
                name="Sales", marker_color=COLORS["primary"],
                marker=dict(cornerradius=6),
            ))
            fig_bar.add_trace(go.Bar(
                x=div_agg["Division"], y=div_agg["Gross Profit"],
                name="Gross Profit", marker_color=COLORS["secondary"],
                marker=dict(cornerradius=6),
            ))
            fig_bar.update_layout(
                barmode="group", template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.markdown("### Profit Composition")
            product_profit = (
                filtered_df.groupby("Product Name")["Gross Profit"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            fig_pie = px.pie(
                product_profit, names="Product Name", values="Gross Profit",
                color_discrete_sequence=CHART_COLORS,
                hole=0.5,
            )
            fig_pie.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                height=380,
                legend=dict(font=dict(size=11)),
            )
            fig_pie.update_traces(textinfo="percent+label", textfont_size=11)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Sales trend by region
        st.markdown("### Sales & Profit by Region")
        reg_agg = filtered_df.groupby("Region")[["Sales", "Gross Profit", "Cost"]].sum().reset_index()
        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(
            x=reg_agg["Region"], y=reg_agg["Sales"],
            name="Sales", marker_color=COLORS["primary"],
            marker=dict(cornerradius=6),
        ))
        fig_region.add_trace(go.Bar(
            x=reg_agg["Region"], y=reg_agg["Gross Profit"],
            name="Gross Profit", marker_color=COLORS["success"],
            marker=dict(cornerradius=6),
        ))
        fig_region.add_trace(go.Bar(
            x=reg_agg["Region"], y=reg_agg["Cost"],
            name="Cost", marker_color=COLORS["danger"],
            marker=dict(cornerradius=6),
        ))
        fig_region.update_layout(
            barmode="group", template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # ──────────────────────────────────────────────────────────
    # TAB 2 — Product Analysis
    # ──────────────────────────────────────────────────────────
    with tab_products:
        profit_df = compute_profit_metrics(filtered_df)

        st.markdown("### Profitability Metrics by Product")
        st.dataframe(
            profit_df.style.format({
                "Gross Profit": "${:,.2f}",
                "Sales": "${:,.2f}",
                "Cost": "${:,.2f}",
                "Gross Margin (%)": "{:.2f}%",
                "Profit per Unit": "${:.2f}",
                "Cost per Unit": "${:.2f}",
                "Profit Contribution (%)": "{:.2f}%",
                "Profit (%)": "{:.2f}%",
            }).background_gradient(
                subset=["Gross Margin (%)"], cmap="viridis", vmin=0, vmax=100
            ).background_gradient(
                subset=["Profit Contribution (%)"], cmap="magma", vmin=0
            ),
            use_container_width=True,
            height=400,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### Top Products by Gross Profit")
            top_profit = profit_df.nlargest(10, "Gross Profit")
            fig_top = px.bar(
                top_profit, x="Gross Profit", y="Product Name",
                orientation="h", color="Gross Margin (%)",
                color_continuous_scale="Viridis",
            )
            fig_top.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis=dict(autorange="reversed"),
                height=420,
            )
            st.plotly_chart(fig_top, use_container_width=True)

        with col_b:
            st.markdown("### Margin vs Profit Scatter")
            fig_scatter = px.scatter(
                profit_df, x="Gross Margin (%)", y="Gross Profit",
                size="Units", color="Product Name",
                color_discrete_sequence=CHART_COLORS,
                hover_data=["Product ID", "Sales"],
            )
            fig_scatter.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                height=420,
                showlegend=False,
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Profit per unit vs cost per unit
        st.markdown("### Unit Economics: Profit per Unit vs Cost per Unit")
        fig_unit = go.Figure()
        fig_unit.add_trace(go.Bar(
            x=profit_df["Product Name"], y=profit_df["Profit per Unit"],
            name="Profit / Unit", marker_color=COLORS["success"],
            marker=dict(cornerradius=6),
        ))
        fig_unit.add_trace(go.Bar(
            x=profit_df["Product Name"], y=profit_df["Cost per Unit"],
            name="Cost / Unit", marker_color=COLORS["danger"],
            marker=dict(cornerradius=6),
        ))
        fig_unit.update_layout(
            barmode="group", template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
        )
        st.plotly_chart(fig_unit, use_container_width=True)

    # ──────────────────────────────────────────────────────────
    # TAB 3 — Division & Region
    # ──────────────────────────────────────────────────────────
    with tab_divisions:
        div_metrics = compute_division_metrics(filtered_df)
        reg_metrics = compute_region_metrics(filtered_df)

        st.markdown("### Division Performance")
        st.dataframe(
            div_metrics.style.format({
                "Sales": "${:,.2f}",
                "Gross Profit": "${:,.2f}",
                "Cost": "${:,.2f}",
                "Average Margin (%)": "{:.2f}%",
                "Revenue Share (%)": "{:.2f}%",
                "Profit Share (%)": "{:.2f}%",
            }).background_gradient(
                subset=["Average Margin (%)"], cmap="viridis", vmin=0, vmax=100
            ),
            use_container_width=True,
        )

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("### Revenue vs Profit Share")
            fig_imbalance = go.Figure()
            fig_imbalance.add_trace(go.Bar(
                x=div_metrics["Division"], y=div_metrics["Revenue Share (%)"],
                name="Revenue Share", marker_color=COLORS["primary"],
                marker=dict(cornerradius=6),
            ))
            fig_imbalance.add_trace(go.Bar(
                x=div_metrics["Division"], y=div_metrics["Profit Share (%)"],
                name="Profit Share", marker_color=COLORS["accent"],
                marker=dict(cornerradius=6),
            ))
            fig_imbalance.update_layout(
                barmode="group", template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                yaxis_title="Share (%)",
            )
            st.plotly_chart(fig_imbalance, use_container_width=True)

        with col_d2:
            st.markdown("### Average Margin by Division")
            fig_margin = px.bar(
                div_metrics, x="Division", y="Average Margin (%)",
                color="Average Margin (%)",
                color_continuous_scale="Viridis",
            )
            fig_margin.update_layout(
                template=PLOTLY_TEMPLATE,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                height=380,
            )
            fig_margin.update_traces(marker=dict(cornerradius=6))
            st.plotly_chart(fig_margin, use_container_width=True)

        st.markdown("---")
        st.markdown("### Region Performance")
        st.dataframe(
            reg_metrics.style.format({
                "Sales": "${:,.2f}",
                "Gross Profit": "${:,.2f}",
                "Cost": "${:,.2f}",
                "Average Margin (%)": "{:.2f}%",
                "Revenue Share (%)": "{:.2f}%",
                "Profit Share (%)": "{:.2f}%",
            }).background_gradient(
                subset=["Average Margin (%)"], cmap="viridis", vmin=0, vmax=100
            ),
            use_container_width=True,
        )

        # Radar chart for regions
        st.markdown("### Region Comparison Radar")
        radar_cats = ["Sales", "Gross Profit", "Cost", "Units"]
        fig_radar = go.Figure()
        for i, row in reg_metrics.iterrows():
            max_vals = reg_metrics[radar_cats].max()
            normalized = [(row[c] / max_vals[c] * 100) if max_vals[c] > 0 else 0 for c in radar_cats]
            fig_radar.add_trace(go.Scatterpolar(
                r=normalized + [normalized[0]],
                theta=radar_cats + [radar_cats[0]],
                fill="toself",
                name=row["Region"],
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)]),
                opacity=0.7,
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 110]),
            ),
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=60, r=60, t=30, b=30),
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ──────────────────────────────────────────────────────────
    # TAB 4 — Pareto Analysis
    # ──────────────────────────────────────────────────────────
    with tab_pareto:
        pareto = compute_product_pareto(filtered_df)
        rev_df = pareto['revenue_df']
        prof_df = pareto['profit_df']

        # KPI row
        p1, p2, p3 = st.columns(3)
        p1.metric("Products for 80% Revenue", f"{pareto['products_80_rev']} / {pareto['total_products']}")
        p2.metric("Products for 80% Profit", f"{pareto['products_80_profit']} / {pareto['total_products']}")
        p3.metric("Concentration", f"{pareto['pct_80_rev']:.0f}% of products")

        st.markdown("---")
        col_pr1, col_pr2 = st.columns(2)

        with col_pr1:
            st.markdown("### Revenue Pareto")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=rev_df['Product Name'], y=rev_df['Revenue Share (%)'],
                name='Revenue Share', marker_color=[COLORS['primary'] if i < pareto['products_80_rev'] else '#555' for i in range(len(rev_df))],
                marker=dict(cornerradius=6),
            ))
            fig.add_trace(go.Scatter(
                x=rev_df['Product Name'], y=rev_df['Cumulative Revenue (%)'],
                name='Cumulative %', mode='lines+markers', yaxis='y2',
                line=dict(color=COLORS['accent'], width=3), marker=dict(size=7),
            ))
            fig.add_hline(y=80, line_dash='dash', line_color=COLORS['danger'], annotation_text='80%', yref='y2')
            fig.update_layout(
                template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=80), height=420,
                yaxis=dict(title='Share (%)'), yaxis2=dict(title='Cumulative (%)', overlaying='y', side='right', range=[0, 105]),
                legend=dict(orientation='h', y=1.08), xaxis_tickangle=-45,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_pr2:
            st.markdown("### Profit Pareto")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=prof_df['Product Name'], y=prof_df['Profit Share (%)'],
                name='Profit Share', marker_color=[COLORS['secondary'] if i < pareto['products_80_profit'] else '#555' for i in range(len(prof_df))],
                marker=dict(cornerradius=6),
            ))
            fig2.add_trace(go.Scatter(
                x=prof_df['Product Name'], y=prof_df['Cumulative Profit (%)'],
                name='Cumulative %', mode='lines+markers', yaxis='y2',
                line=dict(color=COLORS['accent'], width=3), marker=dict(size=7),
            ))
            fig2.add_hline(y=80, line_dash='dash', line_color=COLORS['danger'], annotation_text='80%', yref='y2')
            fig2.update_layout(
                template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=80), height=420,
                yaxis=dict(title='Share (%)'), yaxis2=dict(title='Cumulative (%)', overlaying='y', side='right', range=[0, 105]),
                legend=dict(orientation='h', y=1.08), xaxis_tickangle=-45,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Revenue vs Profit share comparison
        st.markdown("### Revenue Share vs Profit Share by Product")
        merged = rev_df[['Product Name', 'Revenue Share (%)']].merge(
            prof_df[['Product Name', 'Profit Share (%)']], on='Product Name'
        )
        merged['Gap'] = merged['Profit Share (%)'] - merged['Revenue Share (%)']
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=merged['Product Name'], y=merged['Revenue Share (%)'], name='Revenue Share', marker_color=COLORS['primary'], marker=dict(cornerradius=6)))
        fig3.add_trace(go.Bar(x=merged['Product Name'], y=merged['Profit Share (%)'], name='Profit Share', marker_color=COLORS['success'], marker=dict(cornerradius=6)))
        fig3.update_layout(
            barmode='group', template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=80), height=380, xaxis_tickangle=-45,
            legend=dict(orientation='h', y=1.08),
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Key findings
        st.markdown("### 🔍 Key Findings")
        col_f1, col_f2 = st.columns(2)
        col_f1.success(f"**{pareto['pct_80_rev']:.1f}%** of products generate **80%** of revenue")
        col_f2.success(f"**{pareto['pct_80_profit']:.1f}%** of products generate **80%** of profit")

    # ──────────────────────────────────────────────────────────
    # TAB 5 — Geographic Risk
    # ──────────────────────────────────────────────────────────
    with tab_geo:
        geo = compute_state_congestion(filtered_df)
        reg = geo['region_df']
        states = geo['state_df']

        g1, g2, g3 = st.columns(3)
        g1.metric("States for 80% Orders", f"{geo['states_80']} / {geo['total_states']}")
        g2.metric("Regional HHI", f"{geo['region_hhi']:.0f}", delta="HIGH" if geo['region_hhi'] > 2500 else "MODERATE" if geo['region_hhi'] > 1500 else "LOW")
        g3.metric("Top Region", f"{reg.iloc[0]['Region']} ({reg.iloc[0]['Revenue Share (%)']:.1f}%)")

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("### Regional Distribution")
            fig_pie = px.pie(reg, names='Region', values='Total_Orders', color_discrete_sequence=CHART_COLORS, hole=0.45)
            fig_pie.update_layout(template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20), height=380)
            fig_pie.update_traces(textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g2:
            st.markdown("### Congestion Density (Orders/State)")
            fig_cong = px.bar(reg.sort_values('Orders per State', ascending=True), x='Orders per State', y='Region',
                              orientation='h', color='Orders per State', color_continuous_scale='Reds')
            fig_cong.update_layout(template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   margin=dict(l=20, r=20, t=30, b=20), height=380)
            fig_cong.update_traces(marker=dict(cornerradius=6))
            st.plotly_chart(fig_cong, use_container_width=True)

        # Top congestion states
        st.markdown("### Top 15 Congestion-Prone States")
        top_states = states.head(15).copy()
        risk_colors_map = {'HIGH': COLORS['danger'], 'MEDIUM': COLORS['warning'], 'LOW': COLORS['success']}
        fig_states = go.Figure()
        for risk in ['HIGH', 'MEDIUM', 'LOW']:
            mask = top_states[top_states['Risk'] == risk]
            if not mask.empty:
                fig_states.add_trace(go.Bar(
                    y=[f"{r['State/Province']} ({r['Region']})" for _, r in mask.iterrows()],
                    x=mask['Order Share (%)'], orientation='h', name=f'{risk} Risk',
                    marker_color=risk_colors_map[risk], marker=dict(cornerradius=6),
                ))
        fig_states.update_layout(
            barmode='stack', template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20), height=450, xaxis_title='Order Share (%)',
            legend=dict(orientation='h', y=1.08),
        )
        st.plotly_chart(fig_states, use_container_width=True)

        # Risk summary
        st.markdown("### 🔍 Dependency Risk")
        high_count = len(states[states['Risk'] == 'HIGH'])
        med_count = len(states[states['Risk'] == 'MEDIUM'])
        rc1, rc2, rc3 = st.columns(3)
        rc1.error(f"**{high_count}** HIGH risk states (≥5% of orders)")
        rc2.warning(f"**{med_count}** MEDIUM risk states (2-5%)")
        hhi_level = "HIGH" if geo['region_hhi'] > 2500 else "MODERATE" if geo['region_hhi'] > 1500 else "LOW"
        rc3.info(f"Regional HHI: **{geo['region_hhi']:.0f}** ({hhi_level})")

    # ──────────────────────────────────────────────────────────
    # TAB 6 — Cost Diagnostics
    # ──────────────────────────────────────────────────────────
    with tab_cost:
        cost_df, overall_margin_val = compute_cost_diagnostics(filtered_df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Margin", f"{overall_margin_val:.1f}%")
        c2.metric("Lowest Margin", f"{cost_df['Margin (%)'].min():.1f}%", delta=cost_df.loc[cost_df['Margin (%)'].idxmin(), 'Product Name'])
        c3.metric("Highest Margin", f"{cost_df['Margin (%)'].max():.1f}%", delta=cost_df.loc[cost_df['Margin (%)'].idxmax(), 'Product Name'])
        c4.metric("Margin Spread", f"{cost_df['Margin (%)'].max() - cost_df['Margin (%)'].min():.1f}pp")

        st.markdown("---")

        # Cost vs Sales Scatter
        st.markdown("### Cost vs Sales Scatter")
        fig_scat = px.scatter(
            cost_df, x='Total_Sales', y='Total_Cost', size='Total_Units',
            color='Margin (%)', color_continuous_scale='RdYlGn',
            hover_name='Product Name', hover_data=['Margin (%)', 'Markup (%)'],
            size_max=50,
        )
        max_v = max(cost_df['Total_Sales'].max(), cost_df['Total_Cost'].max()) * 1.1
        fig_scat.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v], mode='lines', name='Break-even', line=dict(dash='dash', color='gray')))
        fig_scat.update_layout(
            template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20), height=450,
            xaxis_title='Total Sales ($)', yaxis_title='Total Cost ($)',
        )
        st.plotly_chart(fig_scat, use_container_width=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            # Cost-Margin Quadrant
            st.markdown("### Cost-Margin Quadrant")
            overall_cost_ratio = 100 - overall_margin_val
            fig_quad = px.scatter(
                cost_df, x='Cost Ratio (%)', y='Margin (%)', size='Revenue Share (%)',
                color='Markup (%)', color_continuous_scale='RdYlGn',
                hover_name='Product Name', size_max=40,
            )
            fig_quad.add_hline(y=overall_margin_val, line_dash='dash', line_color='white', opacity=0.4)
            fig_quad.add_vline(x=overall_cost_ratio, line_dash='dash', line_color='white', opacity=0.4)
            fig_quad.update_layout(
                template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20), height=420,
                xaxis=dict(range=[0, 100]), yaxis=dict(range=[0, 100]),
            )
            st.plotly_chart(fig_quad, use_container_width=True)

        with col_c2:
            # Margin lollipop
            st.markdown("### Product Margins & Actions")
            sorted_cost = cost_df.sort_values('Margin (%)', ascending=True)
            action_colors = {'Discontinuation Review': COLORS['danger'], 'Cost Renegotiation': COLORS['warning'],
                             'Repricing': '#fbbf24', 'No Action Needed': COLORS['success']}
            colors_list = [action_colors.get(a, COLORS['primary']) for a in sorted_cost['Primary Action']]
            fig_lol = go.Figure()
            fig_lol.add_trace(go.Bar(
                y=sorted_cost['Product Name'], x=sorted_cost['Margin (%)'],
                orientation='h', marker_color=colors_list, marker=dict(cornerradius=6),
                text=[f"{m:.1f}%" for m in sorted_cost['Margin (%)']], textposition='outside',
            ))
            fig_lol.add_vline(x=overall_margin_val, line_dash='dash', line_color='white', opacity=0.5,
                              annotation_text=f'Avg {overall_margin_val:.1f}%')
            fig_lol.update_layout(
                template=PLOTLY_TEMPLATE, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20), height=420, showlegend=False,
                xaxis=dict(range=[0, 95]),
            )
            st.plotly_chart(fig_lol, use_container_width=True)

        # Action flags table
        st.markdown("### 🏷️ Product Action Summary")
        display_cost = cost_df[['Product Name', 'Avg Price/Unit', 'Avg Cost/Unit', 'Margin (%)',
                                'Markup (%)', 'Revenue Share (%)', 'Action']].copy()
        display_cost = display_cost.sort_values('Margin (%)')
        st.dataframe(
            display_cost.style.format({
                'Avg Price/Unit': '${:.2f}', 'Avg Cost/Unit': '${:.2f}',
                'Margin (%)': '{:.1f}%', 'Markup (%)': '{:.0f}%', 'Revenue Share (%)': '{:.1f}%',
            }).background_gradient(subset=['Margin (%)'], cmap='RdYlGn', vmin=0, vmax=100),
            use_container_width=True, height=400,
        )

        # Action counts
        st.markdown("### 🔍 Action Summary")
        ac1, ac2, ac3, ac4 = st.columns(4)
        disc_count = cost_df['Action'].str.contains('Discontinuation').sum()
        cost_neg_count = cost_df['Action'].str.contains('Cost Renegotiation').sum()
        reprice_count = cost_df['Action'].str.contains('Repricing').sum()
        ok_count = cost_df['Action'].str.contains('No Action').sum()
        ac1.error(f"🔴 **{disc_count}** Discontinuation Review")
        ac2.warning(f"🟠 **{cost_neg_count}** Cost Renegotiation")
        ac3.info(f"🟡 **{reprice_count}** Repricing Needed")
        ac4.success(f"✅ **{ok_count}** No Action Needed")

    # ──────────────────────────────────────────────────────────
    # TAB 7 — Raw Data
    # ──────────────────────────────────────────────────────────
    with tab_data:
        st.markdown("### 📋 Filtered Dataset")
        st.markdown(
            f"<p style='color:#8888aa;'>Showing <b>{len(filtered_df):,}</b> of "
            f"<b>{len(df):,}</b> records</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(filtered_df, use_container_width=True, height=500)

        # Download button
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Download Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_profit_data.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
