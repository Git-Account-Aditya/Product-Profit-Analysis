import streamlit as st

from styles import CUSTOM_CSS
from data_loader import load_data
from metrics import compute_overall_kpis
from components import kpi_card, kpi_grid

from modules import product_profitability, division_performance, cost_diagnostics
from modules import profit_concentration, raw_data

# Page Config
st.set_page_config(
    page_title="Product Profit Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Main
def main():
    df = load_data()
    
    #  SIDEBAR — All User Capabilities
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;margin-bottom:20px;">
            <h2 style="margin:4px 0 0 0;font-size:1.1rem;background:linear-gradient(135deg,#a78bfa,#06b6d4);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;">
                Profit Analyzer
            </h2>
            <p style="color:#6b7280;font-size:0.72rem;margin-top:2px;">Nassau Candy Distributor</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 1) Date Range Selector
        st.markdown('<p class="filter-label">Date Range</p>', unsafe_allow_html=True)
        min_date = df["Order Date"].min().date()
        max_date = df["Order Date"].max().date()
        date_range = st.date_input(
            "Order Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range",
            label_visibility="collapsed",
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

        st.markdown("---")

        # 2) Division Filter
        st.markdown('<p class="filter-label">Division</p>', unsafe_allow_html=True)
        all_divisions = sorted(df["Division"].unique())
        selected_divisions = st.multiselect(
            "Division", options=all_divisions, default=all_divisions,
            key="div_filter", label_visibility="collapsed",
        )

        # 3) Margin Threshold Slider
        st.markdown('<p class="filter-label">Margin Threshold</p>', unsafe_allow_html=True)
        margin_threshold = st.slider(
            "Minimum Gross Margin (%)", min_value=0, max_value=100, value=0, step=1,
            key="margin_slider",
            help="Filter products to show only those with gross margin above this threshold.",
            label_visibility="collapsed",
        )
        st.caption(f"Showing products with margin ≥ **{margin_threshold}%**")

        # 4) Product Search
        st.markdown('<p class="filter-label">Product Search</p>', unsafe_allow_html=True)
        product_search = st.text_input(
            "Search Products", value="", placeholder="Type product name...",
            key="product_search", label_visibility="collapsed",
        )

        st.markdown("---")

        # Additional Filters
        st.markdown('<p class="filter-label">Region</p>', unsafe_allow_html=True)
        all_regions = sorted(df["Region"].unique())
        selected_regions = st.multiselect(
            "Region", options=all_regions, default=all_regions,
            key="reg_filter", label_visibility="collapsed",
        )

        st.markdown('<p class="filter-label">Ship Mode</p>', unsafe_allow_html=True)
        all_ship_modes = sorted(df["Ship Mode"].unique())
        selected_ship_modes = st.multiselect(
            "Ship Mode", options=all_ship_modes, default=all_ship_modes,
            key="ship_filter", label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            "<p style='color:#4b5563;font-size:0.7rem;text-align:center;'>"
            "Built with Streamlit & Plotly<br>Nassau Candy Distributor © 2024</p>",
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════════════════════
    #  Apply Filters
    # ══════════════════════════════════════════════════════════
    filtered_df = df[
        (df["Order Date"].dt.date >= start_date)
        & (df["Order Date"].dt.date <= end_date)
        & (df["Division"].isin(selected_divisions))
        & (df["Region"].isin(selected_regions))
        & (df["Ship Mode"].isin(selected_ship_modes))
    ]

    if product_search.strip():
        product_filtered_df = filtered_df[
            filtered_df["Product Name"].str.contains(product_search.strip(), case=False, na=False)
        ]
    else:
        product_filtered_df = filtered_df

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your filters.")
        return

    # ══════════════════════════════════════════════════════════
    #  Hero Header
    # ══════════════════════════════════════════════════════════
    st.markdown("""
    <div class="hero-header">
        <h1>Product Profit Analyzer</h1>
        <p class="hero-subtitle">Nassau Candy Distributor — Interactive Profitability Intelligence Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  Global KPI Grid (all 5 requested + extras)
    # ══════════════════════════════════════════════════════════
    kpis = compute_overall_kpis(filtered_df)

    kpi_grid([
        kpi_card("Total Revenue", f"${kpis['total_sales']:,.0f}"),
        kpi_card("Gross Profit", f"${kpis['total_profit']:,.0f}"),
        kpi_card("Total Cost", f"${kpis['total_cost']:,.0f}"),
        kpi_card("Units Sold", f"{kpis['total_units']:,}"),
        kpi_card("Gross Margin", f"{kpis['avg_margin']:.1f}%",
                 "Gross Profit ÷ Sales", "neutral"),
        kpi_card("Profit / Unit", f"${kpis['profit_per_unit']:.2f}",
                 "Gross Profit ÷ Units", "neutral"),
        kpi_card("Products", f"{kpis['num_products']}"),
        kpi_card("Margin Volatility", f"{kpis['margin_volatility']:.2f}%",
                 "Low" if kpis["margin_volatility"] < 3 else ("Moderate" if kpis["margin_volatility"] < 8 else "High"),
                 "positive" if kpis["margin_volatility"] < 3 else ("neutral" if kpis["margin_volatility"] < 8 else "negative")),
    ])

    st.markdown("")

    # ══════════════════════════════════════════════════════════
    #  Navigation Tabs → Page Modules
    # ══════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Product Profitability",
        "Division Performance",
        "Cost vs Margin Diagnostics",
        "Profit Concentration",
        "Raw Data",
    ])

    with tab1:
        product_profitability.render(
            filtered_df, product_filtered_df,
            margin_threshold, product_search, kpis["avg_margin"],
        )

    with tab2:
        division_performance.render(filtered_df, kpis["avg_margin"])

    with tab3:
        cost_diagnostics.render(filtered_df, margin_threshold)

    with tab4:
        profit_concentration.render(filtered_df)

    with tab5:
        raw_data.render(filtered_df, df, start_date, end_date, selected_divisions)


if __name__ == "__main__":
    main()
