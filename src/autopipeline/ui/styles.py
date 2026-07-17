"""Premium dark theme — inspired by Linear, Stripe, Vercel."""

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* === FOUNDATION === */
:root {
    --bg-primary: #09090b;
    --bg-secondary: #18181b;
    --bg-tertiary: #27272a;
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --text-primary: #fafafa;
    --text-secondary: #a1a1aa;
    --text-tertiary: #71717a;
    --accent: #6366f1;
    --accent-soft: rgba(99,102,241,0.12);
    --success: #22c55e;
    --success-soft: rgba(34,197,94,0.12);
    --warning: #eab308;
    --warning-soft: rgba(234,179,8,0.12);
    --danger: #ef4444;
    --danger-soft: rgba(239,68,68,0.12);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.5);
}

.stApp {
    background: var(--bg-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: var(--text-secondary) !important;
}

/* === TYPOGRAPHY === */
h1 { font-size: 1.5rem !important; font-weight: 600 !important; letter-spacing: -0.025em !important; }
h2 { font-size: 1.125rem !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }
h3 { font-size: 0.875rem !important; font-weight: 500 !important; }

/* === GLASS CARD === */
.glass-card {
    background: rgba(24,24,27,0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.glass-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-md);
}

/* === KPI CARD === */
.kpi-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.kpi-card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 0 0 1px var(--border-hover), var(--shadow-sm);
}
.kpi-card:hover::after { opacity: 0.6; }

.kpi-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--text-tertiary);
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}
.kpi-change {
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 6px;
}
.kpi-change.positive { color: var(--success); }
.kpi-change.negative { color: var(--danger); }

/* === STATUS === */
.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    vertical-align: middle;
}
.status-indicator.live {
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: statusPulse 3s ease-in-out infinite;
}
.status-indicator.warn {
    background: var(--warning);
    box-shadow: 0 0 6px var(--warning);
}
.status-indicator.err {
    background: var(--danger);
    box-shadow: 0 0 6px var(--danger);
}

@keyframes statusPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* === ANIMATIONS === */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-8px); }
    to { opacity: 1; transform: translateX(0); }
}

.anim-fade-up { animation: fadeInUp 0.4s ease-out forwards; opacity: 0; }
.anim-fade { animation: fadeIn 0.3s ease-out forwards; opacity: 0; }
.anim-slide-left { animation: slideInLeft 0.3s ease-out forwards; opacity: 0; }

.delay-1 { animation-delay: 0.05s; }
.delay-2 { animation-delay: 0.1s; }
.delay-3 { animation-delay: 0.15s; }
.delay-4 { animation-delay: 0.2s; }

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-secondary);
    border-radius: var(--radius-sm);
    padding: 3px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 16px;
    color: var(--text-tertiary);
    font-weight: 500;
    font-size: 0.85rem;
    transition: all 0.15s ease;
    border: none;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-sm);
}

/* === BUTTONS === */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-secondary) !important;
    color: var(--text-secondary) !important;
}
.stButton > button:hover {
    border-color: var(--border-hover) !important;
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    filter: brightness(1.1);
    box-shadow: 0 0 16px var(--accent-soft);
}

/* === INPUTS === */
.stSelectbox, .stTextInput, .stTextArea, .stSlider {
    border-radius: var(--radius-sm) !important;
}

/* === SECTION HEADER === */
.section-header {
    font-size: 0.6875rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    font-weight: 600;
    margin-bottom: 12px;
}

/* === EMPTY STATE === */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-tertiary);
}
.empty-state-icon {
    font-size: 2rem;
    margin-bottom: 12px;
    opacity: 0.5;
}
.empty-state-text {
    font-size: 0.875rem;
    font-weight: 500;
}
.empty-state-sub {
    font-size: 0.8rem;
    margin-top: 4px;
    opacity: 0.7;
}

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg-tertiary); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
