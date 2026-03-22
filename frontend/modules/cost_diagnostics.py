import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COLORS, styled_layout
from analysis_helpers import compute_cost_diagnostics
from components import module_header, insight_callout


def render(filtered_df, margin_threshold):
    """Render the Cost vs Margin Diagnostics tab."""

    module_header(
        "", "pink", "Cost vs Margin Diagnostics",
        "Cost-sales scatter plots & margin risk flags",
    )

    cost_df, overall_margin_val = compute_cost_diagnostics(filtered_df)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Margin", f"{overall_margin_val:.1f}%")
    c2.metric("Lowest Margin",
              f"{cost_df['Margin (%)'].min():.1f}%",
              delta=cost_df.loc[cost_df["Margin (%)"].idxmin(), "Product Name"])
    c3.metric("Highest Margin",
              f"{cost_df['Margin (%)'].max():.1f}%",
              delta=cost_df.loc[cost_df["Margin (%)"].idxmax(), "Product Name"])
    c4.metric("Margin Spread",
              f"{cost_df['Margin (%)'].max() - cost_df['Margin (%)'].min():.1f}pp")

    st.markdown("---")

    # ── Cost vs Sales Scatter ──
    st.markdown("### Cost vs Sales Scatter Plot")
    fig_scat = px.scatter(
        cost_df, x="Total_Sales", y="Total_Cost", size="Total_Units",
        color="Margin (%)", color_continuous_scale="RdYlGn",
        hover_name="Product Name",
        hover_data={"Margin (%)": ":.1f", "Markup (%)": ":.0f",
                    "Total_Sales": ":$,.0f", "Total_Cost": ":$,.0f"},
        size_max=55,
    )
    max_v = max(cost_df["Total_Sales"].max(), cost_df["Total_Cost"].max()) * 1.1
    fig_scat.add_trace(go.Scatter(
        x=[0, max_v], y=[0, max_v], mode="lines",
        name="Break-even Line",
        line=dict(dash="dash", color="rgba(255,255,255,0.3)", width=2),
    ))
    fig_scat.add_trace(go.Scatter(
        x=[0, max_v, 0], y=[0, max_v, max_v], fill="toself",
        fillcolor="rgba(248,113,113,0.04)", line=dict(width=0),
        name="Loss Zone", showlegend=True,
    ))
    fig_scat.update_layout(**styled_layout(
        margin=dict(l=20, r=20, t=10, b=20), height=480,
        xaxis_title="Total Sales ($)", yaxis_title="Total Cost ($)",
        legend=dict(orientation="h", y=-0.12),
    ))
    st.plotly_chart(fig_scat, use_container_width=True)

    insight_callout(
        "Products <strong>above</strong> the break-even line are operating at a loss. "
        "Bubble size represents unit volume. Color encodes margin strength."
    )

    st.markdown("---")

    # ── Cost-Margin Quadrant & Margin Risk Flags ──
    st.markdown("### Cost-Margin Quadrant Analysis")
    col_q1, col_q2 = st.columns(2)

    with col_q1:
        overall_cost_ratio = 100 - overall_margin_val
        fig_quad = px.scatter(
            cost_df, x="Cost Ratio (%)", y="Margin (%)",
            size="Revenue Share (%)", color="Markup (%)",
            color_continuous_scale="RdYlGn",
            hover_name="Product Name", size_max=45,
        )
        fig_quad.add_hline(y=overall_margin_val, line_dash="dash",
                           line_color="rgba(255,255,255,0.25)")
        fig_quad.add_vline(x=overall_cost_ratio, line_dash="dash",
                           line_color="rgba(255,255,255,0.25)")
        fig_quad.add_annotation(x=25, y=90, text="Stars", showarrow=False,
                                font=dict(color="#34d399", size=14))
        fig_quad.add_annotation(x=85, y=90, text="Cost-Heavy Winners", showarrow=False,
                                font=dict(color="#fbbf24", size=14))
        fig_quad.add_annotation(x=25, y=5, text="Underperformers", showarrow=False,
                                font=dict(color="#f87171", size=14))
        fig_quad.add_annotation(x=85, y=5, text="Danger Zone", showarrow=False,
                                font=dict(color="#f87171", size=14))
        fig_quad.update_layout(**styled_layout(
            margin=dict(l=20, r=20, t=10, b=20), height=450,
            xaxis=dict(range=[0, 100], title="Cost Ratio (%)"),
            yaxis=dict(range=[0, 100], title="Margin (%)"),
        ))
        st.plotly_chart(fig_quad, use_container_width=True)

    with col_q2:
        st.markdown("#### Margin Risk Flags")
        sorted_cost = cost_df.sort_values("Margin (%)", ascending=True)
        action_colors = {
            "Discontinuation Review": COLORS["danger"],
            "Cost Renegotiation": COLORS["warning"],
            "Repricing": "#fbbf24",
            "No Action Needed": COLORS["success"],
        }
        colors_list = [action_colors.get(a, COLORS["primary"]) for a in sorted_cost["Primary Action"]]

        fig_risk = go.Figure()
        fig_risk.add_trace(go.Bar(
            y=sorted_cost["Product Name"], x=sorted_cost["Margin (%)"],
            orientation="h", marker_color=colors_list,
            marker=dict(cornerradius=8),
            text=[f"{m:.1f}%" for m in sorted_cost["Margin (%)"]],
            textposition="outside", textfont=dict(size=12, color="#e0e7ff"),
        ))
        fig_risk.add_vline(
            x=overall_margin_val, line_dash="dash", line_color="rgba(255,255,255,0.4)",
            annotation_text=f"Avg {overall_margin_val:.1f}%",
            annotation_font_color="#c4b5fd",
            annotation_font_size=13,
        )
        if margin_threshold > 0:
            fig_risk.add_vline(
                x=margin_threshold, line_dash="dot", line_color=COLORS["accent"],
                annotation_text=f"Threshold: {margin_threshold}%",
                annotation_font_color=COLORS["accent"],
                annotation_font_size=13,
            )
        fig_risk.update_layout(**styled_layout(
            margin=dict(l=20, r=80, t=10, b=20), height=450,
            showlegend=False, xaxis=dict(range=[0, 95], title="Margin (%)"),
        ))
        st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("---")

    # ── Action Summary Table ──
    st.markdown("### Product Action Flags")
    display_cost = cost_df[["Product Name", "Avg Price/Unit", "Avg Cost/Unit", "Margin (%)",
                             "Markup (%)", "Revenue Share (%)", "Action"]].copy()
    display_cost = display_cost.sort_values("Margin (%)")
    st.dataframe(
        display_cost.style.format({
            "Avg Price/Unit": "${:.2f}", "Avg Cost/Unit": "${:.2f}",
            "Margin (%)": "{:.1f}%", "Markup (%)": "{:.0f}%",
            "Revenue Share (%)": "{:.1f}%",
        }).background_gradient(subset=["Margin (%)"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True, height=420,
    )

    # Action counts
    st.markdown("### Action Distribution")
    ac1, ac2, ac3, ac4 = st.columns(4)
    disc_count = cost_df["Action"].str.contains("Discontinuation").sum()
    cost_neg_count = cost_df["Action"].str.contains("Cost Renegotiation").sum()
    reprice_count = cost_df["Action"].str.contains("Repricing").sum()
    ok_count = cost_df["Action"].str.contains("No Action").sum()
    ac1.error(f"**{disc_count}** Discontinuation Review")
    ac2.warning(f"**{cost_neg_count}** Cost Renegotiation")
    ac3.info(f"**{reprice_count}** Repricing Needed")
    ac4.success(f"**{ok_count}** No Action Needed")
