"""Dashboard — Overview with KPIs, health chart, timeline."""
import streamlit as st
import plotly.graph_objects as go


def _kpi(value: str, label: str, change: str = "", delay: int = 0):
    cls = f"anim-fade-up delay-{delay}" if delay else "anim-fade-up"
    change_cls = "positive" if change.startswith("+") or change.startswith("↑") else "negative" if change else ""
    change_html = f'<div class="kpi-change {change_cls}">{change}</div>' if change else ""
    st.markdown(f"""
    <div class="kpi-card {cls}">
        <div class="kpi-number">{value}</div>
        <div class="kpi-label">{label}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)


def _donut(healthy: int, warning: int, critical: int):
    total = healthy + warning + critical
    if total == 0:
        healthy, total = 1, 1
    fig = go.Figure(data=[go.Pie(
        labels=["Healthy", "Warning", "Critical"],
        values=[healthy, warning, critical],
        hole=0.78,
        marker_colors=["#22c55e", "#eab308", "#ef4444"],
        textinfo="value",
        textfont_size=13,
        textfont_color="#fafafa",
    )])
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, b=8, l=8, r=8),
        height=180,
    )
    return fig


def _area_chart(history: list[dict]):
    if not history:
        return None
    ts = [h["timestamp"][11:16] for h in history]
    vals = [h.get("issues_found", 0) for h in history]
    fig = go.Figure(data=[go.Scatter(
        x=ts, y=vals,
        mode="lines",
        line=dict(color="#6366f1", width=2, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.06)",
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, b=32, l=36, r=8),
        height=180,
        xaxis=dict(showgrid=False, color="#71717a", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#71717a", tickfont=dict(size=10)),
    )
    return fig


def render():
    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _kpi("1,113", "Datasets", delay=1)
    with c2:
        n = len(st.session_state.issues)
        _kpi(str(n), "Active Issues", f"↑ {n} found" if n else "", delay=2)
    with c3:
        h = st.session_state.healed_count
        _kpi(str(h), "Healed", f"↑ {h} resolved" if h else "", delay=3)
    with c4:
        _kpi(str(len(st.session_state.cycle_history)), "Cycles", delay=4)

    st.markdown("")
    st.markdown('<div class="section-header">Health & Activity</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        issues = len(st.session_state.issues)
        fig = _donut(max(0, 1113 - issues), issues // 2, issues)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if st.session_state.cycle_history:
            fig = _area_chart(st.session_state.cycle_history)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div class="glass-card empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">No cycles recorded</div>
                <div class="empty-state-sub">Click "Run Cycle Now" to begin monitoring</div>
            </div>
            """, unsafe_allow_html=True)
