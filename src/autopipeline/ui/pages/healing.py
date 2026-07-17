"""Healing history — cycle log."""
import streamlit as st


def _cycle_row(cycle: dict):
    ts = cycle.get("timestamp", "")[:19].replace("T", " ")
    healed = cycle.get("healed", 0)
    ok = healed > 0

    st.markdown(f"""
    <div class="glass-card anim-fade-up" style="margin-bottom:8px;padding:16px">
        <div style="display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:10px">
                <span class="status-indicator {'live' if ok else 'err'}"></span>
                <span style="font-weight:500;color:var(--text-primary);font-size:0.875rem">
                    {'Healed' if ok else 'Failed'}
                </span>
                <span style="color:var(--text-tertiary);font-size:0.8rem">
                    {cycle.get('issues_found', 0)} issues · {healed} resolved
                </span>
            </div>
            <span style="color:var(--text-tertiary);font-size:0.75rem">{ts}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown('<div class="section-header">Healing History</div>', unsafe_allow_html=True)

    if not st.session_state.cycle_history:
        st.markdown("""
        <div class="glass-card empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-text">No healing cycles yet</div>
            <div class="empty-state-sub">Run a cycle to see history here</div>
        </div>
        """, unsafe_allow_html=True)
        return

    n = len(st.session_state.cycle_history)
    h = st.session_state.healed_count
    rate = f"{h}/{n}" if n > 0 else "0/0"

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px">
        <div class="kpi-card anim-fade-up delay-1" style="text-align:center;padding:18px">
            <div class="kpi-number" style="font-size:1.5rem">{n}</div>
            <div class="kpi-label">Total Cycles</div>
        </div>
        <div class="kpi-card anim-fade-up delay-2" style="text-align:center;padding:18px">
            <div class="kpi-number" style="font-size:1.5rem">{h}</div>
            <div class="kpi-label">Healed</div>
        </div>
        <div class="kpi-card anim-fade-up delay-3" style="text-align:center;padding:18px">
            <div class="kpi-number" style="font-size:1.5rem">{rate}</div>
            <div class="kpi-label">Success Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for cycle in reversed(st.session_state.cycle_history):
        _cycle_row(cycle)
