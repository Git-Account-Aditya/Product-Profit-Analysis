"""
Module 2 — Division Performance Dashboard
  • Revenue vs profit comparison
  • Margin distribution by division
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, CHART_COLORS, styled_layout
from metrics import compute_division_metrics
from components import module_header, insight_callout


def render(filtered_df, avg_margin):
    """Render the Division Performance tab."""

    module_header(
        "🏢", "cyan", "Division Performance Dashboard",
        "Revenue vs profit comparison & margin distribution by division",
    )

    div_metrics = compute_division_metrics(filtered_df)

    # ── Revenue vs Profit Comparison ──
    st.markdown("### 📊 Revenue vs Profit Comparison")
    col_rv1, col_rv2 = st.columns([3, 2])

    with col_rv1:
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=div_metrics["Division"], y=div_metrics["Sales"],
            name="Revenue", marker_color=COLORS["primary"],
            marker=dict(cornerradius=8), opacity=0.9,
        ))
        fig_comp.add_trace(go.Bar(
            x=div_metrics["Division"], y=div_metrics["Gross Profit"],
            name="Gross Profit", marker_color=COLORS["success"],
            marker=dict(cornerradius=8), opacity=0.9,
        ))
        fig_comp.add_trace(go.Bar(
            x=div_metrics["Division"], y=div_metrics["Cost"],
            name="Cost", marker_color=COLORS["danger"],
            marker=dict(cornerradius=8), opacity=0.7,
        ))
        fig_comp.update_layout(**styled_layout(
            barmode="group", margin=dict(l=20, r=20, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=420, yaxis_title="Amount ($)",
        ))
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_rv2:
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            y=div_metrics["Division"], x=div_metrics["Revenue Share (%)"],
            name="Revenue Share", marker_color=COLORS["primary"],
            orientation="h", marker=dict(cornerradius=6),
        ))
        fig_div.add_trace(go.Bar(
            y=div_metrics["Division"], x=div_metrics["Profit Share (%)"],
            name="Profit Share", marker_color=COLORS["accent"],
            orientation="h", marker=dict(cornerradius=6),
        ))
        fig_div.update_layout(**styled_layout(
            barmode="group", height=420,
            margin=dict(l=20, r=20, t=10, b=20), xaxis_title="Share (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        ))
        st.plotly_chart(fig_div, use_container_width=True)

    # Insight
    div_metrics["Gap (pp)"] = (div_metrics["Profit Share (%)"] - div_metrics["Revenue Share (%)"]).round(2)
    best_div = div_metrics.loc[div_metrics["Gap (pp)"].idxmax()]
    worst_div = div_metrics.loc[div_metrics["Gap (pp)"].idxmin()]
    insight_callout(
        f"💡 <strong>{best_div['Division']}</strong> over-indexes on profit "
        f"(gap: +{best_div['Gap (pp)']:.1f}pp) — "
        f"<strong>{worst_div['Division']}</strong> under-indexes "
        f"(gap: {worst_div['Gap (pp)']:.1f}pp)"
    )

    st.markdown("---")

    # ── Margin Distribution ──
    st.markdown("### 📐 Margin Distribution by Division")
    col_md1, col_md2 = st.columns(2)

    with col_md1:
        prod_by_div = filtered_df.groupby(["Division", "Product Name"]).agg(
            Sales=("Sales", "sum"), Profit=("Gross Profit", "sum")
        ).reset_index()
        prod_by_div["Margin (%)"] = (prod_by_div["Profit"] / prod_by_div["Sales"] * 100).round(2)

        fig_box = px.box(
            prod_by_div, x="Division", y="Margin (%)",
            color="Division", color_discrete_sequence=CHART_COLORS, points="all",
        )
        fig_box.add_hline(
            y=avg_margin, line_dash="dash", line_color="rgba(255,255,255,0.35)",
            annotation_text=f"Overall: {avg_margin:.1f}%",
            annotation_font_color="#c4b5fd",
            annotation_font_size=13,
        )
        fig_box.update_layout(**styled_layout(
            margin=dict(l=20, r=20, t=10, b=20), height=420,
            showlegend=False, yaxis_title="Gross Margin (%)",
        ))
        st.plotly_chart(fig_box, use_container_width=True)

    with col_md2:
        fig_gauge = go.Figure()
        for _, row in div_metrics.iterrows():
            color = COLORS["success"] if row["Average Margin (%)"] >= avg_margin else COLORS["warning"]
            fig_gauge.add_trace(go.Bar(
                y=[row["Division"]], x=[row["Average Margin (%)"]],
                orientation="h", name=row["Division"],
                marker_color=color, marker=dict(cornerradius=8),
                text=f"{row['Average Margin (%)']:.1f}%", textposition="outside",
                textfont=dict(size=13, color="#e0e7ff"), showlegend=False,
            ))
        fig_gauge.add_vline(
            x=avg_margin, line_dash="dash", line_color=COLORS["accent"],
            annotation_text=f"Avg: {avg_margin:.1f}%",
            annotation_font_color=COLORS["accent"],
            annotation_font_size=13,
        )
        fig_gauge.update_layout(**styled_layout(
            margin=dict(l=20, r=80, t=10, b=20), height=420,
            xaxis_title="Average Margin (%)", xaxis=dict(range=[0, 100]),
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Division Summary Table ──
    st.markdown("### 📋 Division Summary")
    st.dataframe(
        div_metrics.style.format({
            "Sales": "${:,.2f}", "Gross Profit": "${:,.2f}", "Cost": "${:,.2f}",
            "Average Margin (%)": "{:.2f}%", "Revenue Share (%)": "{:.2f}%",
            "Profit Share (%)": "{:.2f}%", "Gap (pp)": "{:+.2f}pp",
        }).background_gradient(subset=["Average Margin (%)"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True,
    )

    st.markdown("---")

    # ── Division × Product Heatmap ──
    st.markdown("### 🗺️ Division × Product Margin Heatmap")
    heatmap_data = filtered_df.groupby(["Division", "Product Name"]).agg(
        Sales=("Sales", "sum"), Profit=("Gross Profit", "sum")
    ).reset_index()
    heatmap_data["Margin (%)"] = (heatmap_data["Profit"] / heatmap_data["Sales"] * 100).round(2)
    pivot = heatmap_data.pivot_table(index="Division", columns="Product Name", values="Margin (%)")

    fig_hm = px.imshow(pivot, color_continuous_scale="RdYlGn", aspect="auto",
                       labels=dict(color="Margin (%)"),
                       text_auto=".1f")
    fig_hm.update_traces(textfont=dict(size=12, color="#ffffff"))
    fig_hm.update_layout(**styled_layout(
        margin=dict(l=20, r=20, t=10, b=100), height=350, xaxis_tickangle=-45,
    ))
    st.plotly_chart(fig_hm, use_container_width=True)
