"""Shared CSS and styling for AutoPilot dashboard."""

DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #0a0b0f;
    --surface: #14151c;
    --surface-hover: #1c1d26;
    --border: #23242f;
    --text: #f0f0f3;
    --muted: #6b7280;
    --accent: #6366f1;
    --accent-glow: rgba(99,102,241,0.15);
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.stApp {
    background: var(--bg);
    font-family: 'Inter', -apple-system, sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}

h1, h2, h3 { color: var(--text) !important; font-weight: 600; }

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gradient);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    border-color: var(--accent);
}
.card:hover::before { opacity: 1; }

.kpi-value {
    font-size: 2.8rem;
    font-weight: 700;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}
.kpi-delta {
    font-size: 0.8rem;
    margin-top: 6px;
    font-weight: 500;
}
.kpi-delta.up { color: var(--success); }
.kpi-delta.down { color: var(--danger); }

.pulse-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
    animation: pulse 2s ease-in-out infinite;
}
.pulse-dot.green { background: var(--success); box-shadow: 0 0 8px var(--success); }
.pulse-dot.yellow { background: var(--warning); box-shadow: 0 0 8px var(--warning); }
.pulse-dot.red { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.7; }
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.animate-in {
    animation: fadeSlideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    opacity: 0;
}
.animate-in-delay-1 { animation-delay: 0.1s; }
.animate-in-delay-2 { animation-delay: 0.2s; }
.animate-in-delay-3 { animation-delay: 0.3s; }
.animate-in-delay-4 { animation-delay: 0.4s; }

.section-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    margin-bottom: 12px;
    font-weight: 600;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    color: var(--muted);
    font-weight: 500;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: var(--gradient) !important;
    color: white !important;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
    border: none;
}
.stButton > button[kind="primary"] {
    background: var(--gradient);
}

.stSelectbox, .stTextInput {
    border-radius: 10px;
}
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(DARK_THEME, unsafe_allow_html=True)
