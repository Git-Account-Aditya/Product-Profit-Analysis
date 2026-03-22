import streamlit as st


def module_header(icon: str, icon_class: str, title: str, description: str):
    """Render a styled module header block."""
    st.markdown(f"""
    <div class="module-header">
        <div class="module-icon {icon_class}">{icon}</div>
        <div>
            <p class="module-title">{title}</p>
            <p class="module-desc">{description}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def insight_callout(text: str):
    """Render a styled insight callout box."""
    st.markdown(f'<div class="insight-callout">{text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_class: str = "neutral") -> str:
    """Return HTML for a single KPI card (use inside kpi_grid)."""
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return (
        f'<div class="kpi-card">'
        f'  <div class="kpi-label">{label}</div>'
        f'  <div class="kpi-value">{value}</div>'
        f'  {delta_html}'
        f'</div>'
    )


def kpi_grid(cards: list[str]):
    """Render a responsive grid of KPI cards."""
    html = '<div class="kpi-grid">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)
