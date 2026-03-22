COLORS = {
    "primary": "#8b5cf6",
    "secondary": "#06b6d4",
    "accent": "#f472b6",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "info": "#38bdf8",
    "muted": "#6b7280",
}

CHART_COLORS = [
    "#8b5cf6", "#06b6d4", "#f472b6", "#34d399", "#fbbf24",
    "#f87171", "#a78bfa", "#22d3ee", "#fb923c", "#4ade80",
    "#e879f9", "#38bdf8", "#facc15", "#fb7185", "#2dd4bf",
]

PLOTLY_TEMPLATE = "plotly_dark"

CHART_LAYOUT_DEFAULTS = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#d1d5db"),
    xaxis=dict(
        title_font=dict(size=14, color="#c4b5fd"),
        tickfont=dict(size=12, color="#b4b4cc"),
        gridcolor="rgba(139,92,246,0.08)",
    ),
    yaxis=dict(
        title_font=dict(size=14, color="#c4b5fd"),
        tickfont=dict(size=12, color="#b4b4cc"),
        gridcolor="rgba(139,92,246,0.08)",
    ),
    legend=dict(font=dict(size=12, color="#c4b5fd")),
    coloraxis_colorbar=dict(
        title_font=dict(size=12, color="#c4b5fd"),
        tickfont=dict(size=11, color="#b4b4cc"),
    ),
)

def styled_layout(**kwargs):
    """Return merged Plotly layout dict with global defaults."""
    import copy
    layout = copy.deepcopy(CHART_LAYOUT_DEFAULTS)
    _MERGE_KEYS = {"xaxis", "yaxis", "yaxis2", "font", "legend",
                   "coloraxis_colorbar", "polar"}
    for key, val in kwargs.items():
        if key in _MERGE_KEYS and isinstance(val, dict) and key in layout:
            layout[key].update(val)
        else:
            layout[key] = val
    return layout
