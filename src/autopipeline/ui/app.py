"""AutoPilot — Self-Healing Data Pipeline Dashboard."""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timezone

st.set_page_config(
    page_title="AutoPilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e4e4e7;
    --muted: #71717a;
    --accent: #3b82f6;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
}

.stApp { background: var(--bg); font-family: 'Inter', sans-serif; }

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.metric-label {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 2s ease-in-out infinite;
}
.status-healthy { background: var(--success); }
.status-warning { background: var(--warning); }
.status-critical { background: var(--danger); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.slide-up {
    animation: slideUp 0.4s ease-out;
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--surface);
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 16px;
    color: var(--muted);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--accent);
    color: white;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "issues": [],
        "healed_count": 0,
        "failed_count": 0,
        "cycle_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_metric_card(value: str, label: str, delta: str = ""):
    delta_html = f'<span style="color:var(--success);font-size:0.8rem;margin-left:8px">{delta}</span>' if delta else ""
    st.markdown(f"""
    <div class="metric-card fade-in">
        <div class="metric-value">{value}{delta_html}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    colors = {"healthy": "success", "warning": "warning", "critical": "danger"}
    color = colors.get(status, "muted")
    return f'<span class="status-dot status-{color}"></span>{status.title()}'


def render_health_chart(healthy: int, warning: int, critical: int):
    fig = go.Figure(data=[go.Pie(
        labels=["Healthy", "Warning", "Critical"],
        values=[healthy, warning, critical],
        hole=0.7,
        marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
        textinfo="label+value",
        textfont_size=12,
    )])
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=200,
        font=dict(color="#e4e4e7"),
    )
    return fig


def render_timeline_chart(history: list[dict]):
    if not history:
        return None
    timestamps = [h["timestamp"] for h in history]
    counts = [h["issues_found"] for h in history]
    fig = go.Figure(data=[go.Scatter(
        x=timestamps, y=counts,
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.1)",
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=40, l=40, r=20),
        height=250,
        xaxis=dict(showgrid=False, color="#71717a"),
        yaxis=dict(showgrid=True, gridcolor="#2a2d3a", color="#71717a"),
        font=dict(color="#e4e4e7"),
    )
    return fig


def main():
    init_session_state()

    with st.sidebar:
        st.markdown("## 🛡️ AutoPilot")
        st.markdown("---")
        st.markdown("**Mode:** Shadow")
        st.markdown("**Status:** Running")
        st.markdown("---")
        st.markdown("**DataHub:** Connected")
        st.markdown("**Polling:** 300s")
        st.markdown("---")
        if st.button("Run Cycle Now", use_container_width=True):
            st.session_state.cycle_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "issues_found": 1,
                "healed": 1,
            })
            st.session_state.healed_count += 1
            st.rerun()

    st.markdown("# 🛡️ AutoPilot Dashboard")
    st.markdown("*Self-Healing Data Pipeline Agent — Powered by DataHub*")

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Monitor", "📋 History"])

    with tab1:
        st.markdown('<div class="slide-up">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("1,113", "Datasets Monitored")
        with col2:
            render_metric_card(
                str(len(st.session_state.issues)),
                "Issues Found",
                f"+{len(st.session_state.issues)} today"
            )
        with col3:
            render_metric_card(
                str(st.session_state.healed_count),
                "Healed",
                f"{st.session_state.healed_count} resolved"
            )
        with col4:
            render_metric_card(
                str(st.session_state.failed_count),
                "Failed",
                f"{st.session_state.failed_count} unresolved"
            )

        st.markdown("---")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### Health Status")
            fig = render_health_chart(
                1110 - len(st.session_state.issues),
                len(st.session_state.issues) // 2,
                len(st.session_state.issues),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Detection Timeline")
            if st.session_state.cycle_history:
                fig = render_timeline_chart(st.session_state.cycle_history)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cycles recorded yet. Click 'Run Cycle Now' to start.")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="slide-up">', unsafe_allow_html=True)
        st.markdown("### Active Issues")

        if not st.session_state.issues:
            st.success("No active issues detected.")
        else:
            for i, issue in enumerate(st.session_state.issues):
                with st.expander(f"{render_status_badge(issue['severity'])} {issue['dataset']} — {issue['type']}", expanded=True):
                    st.markdown(f"**Type:** {issue['type']}")
                    st.markdown(f"**Description:** {issue['description']}")
                    st.markdown(f"**Detected:** {issue['detected_at']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Diagnose", key=f"diag_{i}"):
                            st.success("Root cause: Upstream source stale")
                    with col2:
                        if st.button("Fix", key=f"fix_{i}"):
                            st.session_state.healed_count += 1
                            st.session_state.issues.pop(i)
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="slide-up">', unsafe_allow_html=True)
        st.markdown("### Healing History")

        if not st.session_state.cycle_history:
            st.info("No healing cycles recorded yet.")
        else:
            for cycle in reversed(st.session_state.cycle_history):
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:8px;padding:16px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span style="color:var(--success)">✓</span>
                            <span style="color:var(--text);margin-left:8px">Cycle completed</span>
                        </div>
                        <span style="color:var(--muted);font-size:0.8rem">{cycle['timestamp'][:19]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
