"""
Module 1 — Product Profitability Overview
  • Product-level margin leaderboard
  • Profit contribution charts
  • Full KPI table with all 5 requested KPIs
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, CHART_COLORS, styled_layout
from metrics import compute_profit_metrics
from components import module_header, insight_callout, kpi_card, kpi_grid


def render(filtered_df, product_filtered_df, margin_threshold, product_search, avg_margin):
    """Render the Product Profitability tab."""

    module_header(
        "🏷️", "purple", "Product Profitability Overview",
        "Product-level margin leaderboard & profit contribution analysis",
    )

    profit_df = compute_profit_metrics(product_filtered_df)

    # Apply margin threshold filter
    margin_filtered = profit_df[profit_df["Gross Margin (%)"] >= margin_threshold]

    if margin_filtered.empty:
        st.info(f"No products match the margin threshold of {margin_threshold}%. Try lowering the slider.")
        return

    # ── KPI Cards (the 5 requested KPIs shown at glance) ──
    best = margin_filtered.loc[margin_filtered["Gross Margin (%)"].idxmax()]
    worst = margin_filtered.loc[margin_filtered["Gross Margin (%)"].idxmin()]
    avg_vol = margin_filtered["Margin Volatility (%)"].mean()
    max_rev_contrib = margin_filtered.loc[margin_filtered["Revenue Contribution (%)"].idxmax()]
    max_prof_contrib = margin_filtered.loc[margin_filtered["Profit Contribution (%)"].idxmax()]

    kpi_grid([
        kpi_card("Avg. Gross Margin", f"{margin_filtered['Gross Margin (%)'].mean():.1f}%",
                 f"Best: {best['Product Name'][:22]} ({best['Gross Margin (%)']:.1f}%)", "positive"),
        kpi_card("Avg. Profit / Unit", f"${margin_filtered['Profit per Unit'].mean():.2f}",
                 f"Range: ${margin_filtered['Profit per Unit'].min():.2f} – ${margin_filtered['Profit per Unit'].max():.2f}", "neutral"),
        kpi_card("Top Revenue Contributor", f"{max_rev_contrib['Revenue Contribution (%)']:.1f}%",
                 f"{max_rev_contrib['Product Name'][:24]}", "neutral"),
        kpi_card("Top Profit Contributor", f"{max_prof_contrib['Profit Contribution (%)']:.1f}%",
                 f"{max_prof_contrib['Product Name'][:24]}", "neutral"),
        kpi_card("Margin Volatility (Avg)", f"{avg_vol:.2f}%",
                 "Low" if avg_vol < 3 else ("Moderate" if avg_vol < 8 else "High"),
                 "positive" if avg_vol < 3 else ("neutral" if avg_vol < 8 else "negative")),
    ])

    # ── Margin Leaderboard ──
    st.markdown("### 🏆 Product Margin Leaderboard")
    if product_search.strip():
        insight_callout(
            f'🔍 Search active: showing products matching "<strong>{product_search.strip()}</strong>"'
        )

    leaderboard = margin_filtered.sort_values("Gross Margin (%)", ascending=False).copy()
    leaderboard["Rank"] = range(1, len(leaderboard) + 1)

    # Colour by margin tier
    bar_colors = []
    for m in leaderboard["Gross Margin (%)"]:
        if m >= 50:
            bar_colors.append(COLORS["success"])
        elif m >= 30:
            bar_colors.append(COLORS["secondary"])
        elif m >= 15:
            bar_colors.append(COLORS["warning"])
        else:
            bar_colors.append(COLORS["danger"])

    fig_lb = go.Figure()
    fig_lb.add_trace(go.Bar(
        y=leaderboard["Product Name"], x=leaderboard["Gross Margin (%)"],
        orientation="h", marker_color=bar_colors,
        marker=dict(cornerradius=8),
        text=[f"{m:.1f}%" for m in leaderboard["Gross Margin (%)"]],
        textposition="outside", textfont=dict(size=13, color="#e0e7ff"),
    ))
    if margin_threshold > 0:
        fig_lb.add_vline(x=margin_threshold, line_dash="dash", line_color=COLORS["accent"],
                         annotation_text=f"Threshold: {margin_threshold}%",
                         annotation_font_color=COLORS["accent"],
                         annotation_font_size=13)
    avg_m = leaderboard["Gross Margin (%)"].mean()
    fig_lb.add_vline(x=avg_m, line_dash="dot", line_color="rgba(255,255,255,0.35)",
                     annotation_text=f"Avg: {avg_m:.1f}%",
                     annotation_font_color="#c4b5fd",
                     annotation_font_size=13)
    fig_lb.update_layout(**styled_layout(
        margin=dict(l=20, r=80, t=10, b=20),
        height=max(320, len(leaderboard) * 38),
        xaxis_title="Gross Margin (%)", yaxis=dict(autorange="reversed"), showlegend=False,
    ))
    st.plotly_chart(fig_lb, use_container_width=True)

    # Tier summary
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    n_green = sum(1 for m in leaderboard["Gross Margin (%)"] if m >= 50)
    n_cyan = sum(1 for m in leaderboard["Gross Margin (%)"] if 30 <= m < 50)
    n_yellow = sum(1 for m in leaderboard["Gross Margin (%)"] if 15 <= m < 30)
    n_red = sum(1 for m in leaderboard["Gross Margin (%)"] if m < 15)
    col_t1.success(f"🟢 **{n_green}** Premium (≥50%)")
    col_t2.info(f"🔵 **{n_cyan}** Healthy (30-50%)")
    col_t3.warning(f"🟡 **{n_yellow}** At Risk (15-30%)")
    col_t4.error(f"🔴 **{n_red}** Critical (<15%)")

    st.markdown("---")

    # ── Profit Contribution Charts ──
    st.markdown("### 📊 Profit Contribution Analysis")
    col_pc1, col_pc2 = st.columns(2)

    with col_pc1:
        top12 = margin_filtered.nlargest(12, "Profit Contribution (%)")
        fig_donut = px.pie(top12, names="Product Name", values="Profit Contribution (%)",
                           color_discrete_sequence=CHART_COLORS, hole=0.55)
        fig_donut.update_layout(**styled_layout(
            margin=dict(l=10, r=10, t=10, b=10), height=400,
            legend=dict(font=dict(size=11, color="#c4b5fd"), orientation="h", y=-0.15, xanchor="center", x=0.5),
        ))
        fig_donut.update_traces(textinfo="percent+label",
                                textfont=dict(size=12, color="#e0e7ff"),
                                pull=[0.03] * len(top12))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_pc2:
        tree_data = margin_filtered.copy()
        tree_data["Label"] = tree_data["Product Name"].str[:20]
        fig_tree = px.treemap(tree_data, path=["Label"], values="Gross Profit",
                              color="Gross Margin (%)", color_continuous_scale="Viridis",
                              color_continuous_midpoint=avg_margin)
        fig_tree.update_layout(**styled_layout(margin=dict(l=5, r=5, t=5, b=5), height=400))
        fig_tree.update_traces(textinfo="label+value+percent root",
                               textfont=dict(size=13, color="#ffffff"))
        st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    # ── Margin Volatility Chart ──
    st.markdown("### 📉 Margin Volatility by Product")
    vol_sorted = margin_filtered.sort_values("Margin Volatility (%)", ascending=False)
    vol_colors = [COLORS["danger"] if v >= 8 else COLORS["warning"] if v >= 3 else COLORS["success"]
                  for v in vol_sorted["Margin Volatility (%)"]]
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(
        y=vol_sorted["Product Name"], x=vol_sorted["Margin Volatility (%)"],
        orientation="h", marker_color=vol_colors, marker=dict(cornerradius=8),
        text=[f"{v:.2f}%" for v in vol_sorted["Margin Volatility (%)"]],
        textposition="outside", textfont=dict(size=12, color="#e0e7ff"),
    ))
    fig_vol.update_layout(**styled_layout(
        margin=dict(l=20, r=80, t=10, b=20),
        height=max(300, len(vol_sorted) * 34),
        xaxis_title="Margin Volatility (σ %)", showlegend=False,
        yaxis=dict(autorange="reversed"),
    ))
    st.plotly_chart(fig_vol, use_container_width=True)
    insight_callout(
        "📉 <strong>Margin Volatility</strong> measures the month-to-month standard deviation of each product's "
        "gross margin. Higher volatility indicates less predictable profitability."
    )

    st.markdown("---")

    # ── Detailed Metrics Table ──
    st.markdown("### 📋 Detailed Product KPIs")
    display_cols = [
        "Rank", "Product Name", "Gross Margin (%)", "Profit per Unit",
        "Revenue Contribution (%)", "Profit Contribution (%)", "Margin Volatility (%)",
        "Gross Profit", "Sales", "Cost", "Units", "Cost per Unit",
    ]
    st.dataframe(
        leaderboard[display_cols].style.format({
            "Gross Profit": "${:,.2f}", "Sales": "${:,.2f}", "Cost": "${:,.2f}",
            "Gross Margin (%)": "{:.2f}%", "Profit per Unit": "${:.2f}",
            "Cost per Unit": "${:.2f}", "Revenue Contribution (%)": "{:.2f}%",
            "Profit Contribution (%)": "{:.2f}%", "Margin Volatility (%)": "{:.2f}%",
        }).background_gradient(
            subset=["Gross Margin (%)"], cmap="RdYlGn", vmin=0, vmax=100
        ).background_gradient(
            subset=["Profit Contribution (%)"], cmap="magma", vmin=0
        ).background_gradient(
            subset=["Margin Volatility (%)"], cmap="YlOrRd", vmin=0
        ),
        use_container_width=True, height=440,
    )
