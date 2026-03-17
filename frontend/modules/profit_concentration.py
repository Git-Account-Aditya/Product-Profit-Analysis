"""
Module 4 — Profit Concentration Analysis
  • Pareto charts
  • Dependency indicators
"""
import streamlit as st
import plotly.graph_objects as go

from config import COLORS, styled_layout
from analysis_helpers import compute_product_pareto
from components import module_header, insight_callout


def render(filtered_df):
    """Render the Profit Concentration tab."""

    module_header(
        "📊", "green", "Profit Concentration Analysis",
        "Pareto charts & dependency risk indicators",
    )

    pareto = compute_product_pareto(filtered_df)
    rev_df = pareto["revenue_df"]
    prof_df = pareto["profit_df"]

    # KPI row
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Products for 80% Revenue",
              f"{pareto['products_80_rev']} / {pareto['total_products']}")
    p2.metric("Products for 80% Profit",
              f"{pareto['products_80_profit']} / {pareto['total_products']}")
    p3.metric("Revenue Concentration",
              f"{pareto['pct_80_rev']:.0f}%",
              delta="of products drive 80% revenue")
    p4.metric("Profit Concentration",
              f"{pareto['pct_80_profit']:.0f}%",
              delta="of products drive 80% profit")

    st.markdown("---")

    # ── Pareto Charts ──
    st.markdown("### 📈 Pareto Analysis")
    col_pr1, col_pr2 = st.columns(2)

    with col_pr1:
        st.markdown("#### Revenue Pareto")
        fig_rev = go.Figure()
        bar_colors_rev = [
            COLORS["primary"] if i < pareto["products_80_rev"] else "rgba(100,100,120,0.4)"
            for i in range(len(rev_df))
        ]
        fig_rev.add_trace(go.Bar(
            x=rev_df["Product Name"], y=rev_df["Revenue Share (%)"],
            name="Revenue Share", marker_color=bar_colors_rev,
            marker=dict(cornerradius=6),
        ))
        fig_rev.add_trace(go.Scatter(
            x=rev_df["Product Name"], y=rev_df["Cumulative Revenue (%)"],
            name="Cumulative %", mode="lines+markers", yaxis="y2",
            line=dict(color=COLORS["accent"], width=3),
            marker=dict(size=7, color=COLORS["accent"]),
        ))
        fig_rev.add_hline(y=80, line_dash="dash", line_color=COLORS["danger"],
                          annotation_text="80%", yref="y2",
                          annotation_font=dict(size=14, color=COLORS["danger"]))
        fig_rev.update_layout(**styled_layout(
            margin=dict(l=20, r=20, t=10, b=80), height=440,
            yaxis=dict(title="Share (%)"),
            yaxis2=dict(title="Cumulative (%)", overlaying="y", side="right", range=[0, 105],
                        title_font=dict(size=14, color="#c4b5fd"),
                        tickfont=dict(size=12, color="#b4b4cc")),
            legend=dict(orientation="h", y=1.08), xaxis_tickangle=-45,
        ))
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_pr2:
        st.markdown("#### Profit Pareto")
        fig_prof = go.Figure()
        bar_colors_prof = [
            COLORS["secondary"] if i < pareto["products_80_profit"] else "rgba(100,100,120,0.4)"
            for i in range(len(prof_df))
        ]
        fig_prof.add_trace(go.Bar(
            x=prof_df["Product Name"], y=prof_df["Profit Share (%)"],
            name="Profit Share", marker_color=bar_colors_prof,
            marker=dict(cornerradius=6),
        ))
        fig_prof.add_trace(go.Scatter(
            x=prof_df["Product Name"], y=prof_df["Cumulative Profit (%)"],
            name="Cumulative %", mode="lines+markers", yaxis="y2",
            line=dict(color=COLORS["accent"], width=3),
            marker=dict(size=7, color=COLORS["accent"]),
        ))
        fig_prof.add_hline(y=80, line_dash="dash", line_color=COLORS["danger"],
                           annotation_text="80%", yref="y2",
                           annotation_font=dict(size=14, color=COLORS["danger"]))
        fig_prof.update_layout(**styled_layout(
            margin=dict(l=20, r=20, t=10, b=80), height=440,
            yaxis=dict(title="Share (%)"),
            yaxis2=dict(title="Cumulative (%)", overlaying="y", side="right", range=[0, 105],
                        title_font=dict(size=14, color="#c4b5fd"),
                        tickfont=dict(size=12, color="#b4b4cc")),
            legend=dict(orientation="h", y=1.08), xaxis_tickangle=-45,
        ))
        st.plotly_chart(fig_prof, use_container_width=True)

    st.markdown("---")

    # ── Dependency Indicators ──
    st.markdown("### 🎯 Dependency Risk Indicators")

    rev_shares = rev_df["Revenue Share (%)"].values
    product_hhi = (rev_shares ** 2).sum()
    profit_shares = prof_df["Profit Share (%)"].values
    profit_hhi = (profit_shares ** 2).sum()

    def hhi_label(hhi):
        if hhi > 2500:
            return "HIGH", "danger"
        elif hhi > 1500:
            return "MODERATE", "warning"
        return "LOW", "success"

    rev_label, _ = hhi_label(product_hhi)
    prof_label, _ = hhi_label(profit_hhi)

    col_dep1, col_dep2, col_dep3 = st.columns(3)
    col_dep1.metric("Revenue HHI", f"{product_hhi:.0f}", delta=rev_label)
    col_dep2.metric("Profit HHI", f"{profit_hhi:.0f}", delta=prof_label)

    top_product_rev = rev_df.iloc[0]
    col_dep3.metric(
        "Top Product Dependency",
        f"{top_product_rev['Revenue Share (%)']:.1f}% of revenue",
        delta=top_product_rev["Product Name"],
    )

    insight_callout(
        f"📊 <strong>Revenue HHI: {product_hhi:.0f}</strong> ({rev_label} concentration) — "
        f"<strong>Profit HHI: {profit_hhi:.0f}</strong> ({prof_label} concentration). "
        f"{'⚠️ High dependency on few products.' if rev_label != 'LOW' else '✅ Revenue is well-diversified.'}"
    )

    # Revenue vs Profit share gap
    st.markdown("### 📊 Revenue Share vs Profit Share Gap")
    merged = rev_df[["Product Name", "Revenue Share (%)"]].merge(
        prof_df[["Product Name", "Profit Share (%)"]], on="Product Name"
    )
    merged["Gap (pp)"] = (merged["Profit Share (%)"] - merged["Revenue Share (%)"]).round(2)
    merged = merged.sort_values("Gap (pp)")

    fig_gap = go.Figure()
    gap_colors = [COLORS["success"] if g >= 0 else COLORS["danger"] for g in merged["Gap (pp)"]]
    fig_gap.add_trace(go.Bar(
        y=merged["Product Name"], x=merged["Gap (pp)"],
        orientation="h", marker_color=gap_colors,
        marker=dict(cornerradius=8),
        text=[f"{g:+.1f}pp" for g in merged["Gap (pp)"]],
        textposition="outside", textfont=dict(size=12, color="#e0e7ff"),
    ))
    fig_gap.add_vline(x=0, line_color="rgba(255,255,255,0.3)", line_width=1)
    fig_gap.update_layout(**styled_layout(
        margin=dict(l=20, r=80, t=10, b=20),
        height=max(300, len(merged) * 36),
        xaxis_title="Profit Share − Revenue Share (pp)", showlegend=False,
    ))
    st.plotly_chart(fig_gap, use_container_width=True)

    col_ins1, col_ins2 = st.columns(2)
    col_ins1.success(f"**{pareto['pct_80_rev']:.1f}%** of products generate **80%** of revenue")
    col_ins2.success(f"**{pareto['pct_80_profit']:.1f}%** of products generate **80%** of profit")

    st.markdown("---")

    # ── State/Region Congestion Analysis ──
    from analysis_helpers import compute_state_congestion
    st.markdown("### 🏁 State & Regional Congestion Detection")
    st.markdown("Identification of regions and states with disproportionately high order volume.")
    
    congestion = compute_state_congestion(filtered_df)
    state_df = congestion["state_df"].head(10)
    
    col_cg1, col_cg2 = st.columns([1, 1.2])
    
    with col_cg1:
        fig_state = go.Figure()
        risk_colors = {"HIGH": COLORS["danger"], "MEDIUM": COLORS["warning"], "LOW": COLORS["success"]}
        bar_colors_state = [risk_colors.get(r, COLORS["primary"]) for r in state_df["Risk"]]
        
        fig_state.add_trace(go.Bar(
            y=state_df["State/Province"], x=state_df["Order Share (%)"],
            orientation="h", marker_color=bar_colors_state,
            marker=dict(cornerradius=8),
            text=[f"{s:.1f}%" for s in state_df["Order Share (%)"]],
            textposition="outside", textfont=dict(size=12, color="#e0e7ff"),
        ))
        fig_state.update_layout(**styled_layout(
            margin=dict(l=20, r=80, t=10, b=20), height=400,
            xaxis_title="Order Share (%)", yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, state_df["Order Share (%)"].max() * 1.25]),
        ))
        st.plotly_chart(fig_state, use_container_width=True)

    with col_cg2:
        st.markdown("#### Top States Data")
        st.dataframe(
            state_df[["State/Province", "Region", "Total_Orders", "Order Share (%)", "Risk"]].style.applymap(
                lambda x: f"color: {risk_colors.get(x, 'inherit')}; font-weight: bold;" if x in risk_colors else ""
            ),
            use_container_width=True, hide_index=True
        )
    
    insight_callout(
        f"📍 <strong>{congestion['states_80']} out of {congestion['total_states']} states</strong> "
        f"handle 80% of all orders. High concentration in <strong>{state_df.iloc[0]['State/Province']}</strong> "
        f"({state_df.iloc[0]['Order Share (%)']:.1f}%) peaks operational risk."
    )
