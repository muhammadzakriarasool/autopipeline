"""Dashboard overview — KPIs, health chart, timeline."""
import streamlit as st
import plotly.graph_objects as go


def _kpi_card(value: str, label: str, delta: str = "", delay: int = 0):
    cls = f"animate-in animate-in-delay-{delay}" if delay else "animate-in"
    delta_html = ""
    if delta:
        color = "#22c55e" if delta.startswith("+") else "#ef4444"
        delta_html = f'<div class="kpi-delta up" style="color:{color}">{delta}</div>'
    st.markdown(f"""
    <div class="card {cls}">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def _health_chart(healthy: int, warning: int, critical: int):
    total = healthy + warning + critical
    if total == 0:
        healthy = 1
        total = 1
    fig = go.Figure(data=[go.Pie(
        labels=["Healthy", "Warning", "Critical"],
        values=[healthy, warning, critical],
        hole=0.75,
        marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
        textinfo="value",
        textfont_size=14,
        textfont_color="#f0f0f3",
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="#6b7280", size=11), x=0.5, xanchor="center", y=-0.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=30, l=10, r=10),
        height=220,
    )
    return fig


def _timeline_chart(history: list[dict]):
    if not history:
        return None
    ts = [h["timestamp"][:16] for h in history]
    vals = [h.get("issues_found", 0) for h in history]
    fig = go.Figure(data=[go.Scatter(
        x=ts, y=vals,
        mode="lines+markers",
        line=dict(color="#6366f1", width=2.5, shape="spline"),
        marker=dict(size=8, color="#6366f1", line=dict(width=2, color="#14151c")),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=40, l=40, r=10),
        height=220,
        xaxis=dict(showgrid=False, color="#6b7280", tickfont_size=10),
        yaxis=dict(showgrid=True, gridcolor="#23242f", color="#6b7280", tickfont_size=10),
    )
    return fig


def render():
    st.markdown('<div class="section-title">System Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _kpi_card("1,113", "Datasets Monitored", delay=1)
    with c2:
        _kpi_card(str(len(st.session_state.issues)), "Active Issues", delay=2)
    with c3:
        _kpi_card(str(st.session_state.healed_count), "Healed", delay=3)
    with c4:
        _kpi_card(str(len(st.session_state.cycle_history)), "Cycles Run", delay=4)

    st.markdown("")
    st.markdown('<div class="section-title">Health & Activity</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        issues = len(st.session_state.issues)
        healthy = max(0, 1113 - issues)
        _fig = _health_chart(healthy, issues // 2, issues)
        st.plotly_chart(_fig, use_container_width=True)

    with col2:
        if st.session_state.cycle_history:
            _fig = _timeline_chart(st.session_state.cycle_history)
            st.plotly_chart(_fig, use_container_width=True)
        else:
            st.markdown(
                '<div class="card" style="text-align:center;padding:40px;color:#6b7280">'
                'No cycles recorded yet. Click <b>Run Cycle Now</b> to start.</div>',
                unsafe_allow_html=True,
            )
