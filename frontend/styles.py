CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 40%, #16213e 100%);
    }

    /* ── Animated Gradient Header ── */
    .hero-header {
        background: linear-gradient(135deg, rgba(139,92,246,0.12) 0%, rgba(6,182,212,0.08) 50%, rgba(244,114,182,0.08) 100%);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 28px;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(139,92,246,0.05), transparent 30%);
        animation: rotate 8s linear infinite;
    }
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    .hero-header h1 {
        position: relative;
        z-index: 1;
        background: linear-gradient(135deg, #a78bfa 0%, #06b6d4 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        letter-spacing: -1px;
        margin-bottom: 4px !important;
    }
    .hero-subtitle {
        position: relative;
        z-index: 1;
        color: #6b7280;
        font-size: 0.95rem;
        font-weight: 400;
        letter-spacing: 0.5px;
    }

    /* ── Glassmorphism Metric Cards ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30,30,46,0.85) 0%, rgba(45,45,68,0.75) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 16px;
        padding: 22px 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(139,92,246,0.2), inset 0 1px 0 rgba(255,255,255,0.08);
        border-color: rgba(139,92,246,0.45);
    }
    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-size: 0.7rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e0e7ff !important;
        font-weight: 700;
        font-size: 1.6rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        font-weight: 500;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0c18 0%, #141428 50%, #1a1a30 100%);
        border-right: 1px solid rgba(139,92,246,0.12);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #c4b5fd !important;
    }

    /* ── Module Header ── */
    .module-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(139,92,246,0.15);
    }
    .module-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .module-icon.purple { background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(139,92,246,0.1)); }
    .module-icon.cyan   { background: linear-gradient(135deg, rgba(6,182,212,0.25), rgba(6,182,212,0.1)); }
    .module-icon.pink   { background: linear-gradient(135deg, rgba(244,114,182,0.25), rgba(244,114,182,0.1)); }
    .module-icon.green  { background: linear-gradient(135deg, rgba(52,211,153,0.25), rgba(52,211,153,0.1)); }
    .module-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e0e7ff;
        margin: 0;
    }
    .module-desc {
        font-size: 0.78rem;
        color: #6b7280;
        margin: 2px 0 0 0;
    }

    /* ── Insight Callout ── */
    .insight-callout {
        background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,182,212,0.06) 100%);
        border-left: 3px solid #8b5cf6;
        border-radius: 0 12px 12px 0;
        padding: 14px 20px;
        margin: 12px 0;
        color: #c4b5fd;
        font-size: 0.88rem;
    }
    .insight-callout strong { color: #e0e7ff; }

    /* ── KPI Card (custom HTML) ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin: 16px 0 24px 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, rgba(30,30,46,0.8), rgba(45,45,68,0.6));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 14px;
        padding: 18px 20px;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.4);
        box-shadow: 0 12px 36px rgba(139,92,246,0.15);
    }
    .kpi-label {
        color: #9ca3af;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #e0e7ff;
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.72rem;
        margin-top: 4px;
        font-weight: 500;
    }
    .kpi-delta.positive { color: #34d399; }
    .kpi-delta.negative { color: #f87171; }
    .kpi-delta.neutral  { color: #9ca3af; }

    /* ── Headers ── */
    h1 {
        background: linear-gradient(135deg, #a78bfa 0%, #06b6d4 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #c4b5fd !important;
        font-weight: 600 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(139,92,246,0.15) !important;
        margin: 20px 0 !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30,30,46,0.5);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(139,92,246,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 0.85rem;
        color: #9ca3af;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #c4b5fd;
        background: rgba(139,92,246,0.08);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(139,92,246,0.15) !important;
        color: #c4b5fd !important;
    }

    /* ── Sidebar Filter Label ── */
    .filter-label {
        color: #a78bfa;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
    ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.5); }
</style>
"""
