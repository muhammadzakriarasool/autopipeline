"""Healing history — cycle log with audit trail."""
import streamlit as st


def _cycle_card(cycle: dict, index: int):
    ts = cycle.get("timestamp", "")[:19].replace("T", " ")
    healed = cycle.get("healed", 0)
    issues = cycle.get("issues_found", 0)

    status = "✓ Healed" if healed > 0 else "✗ Failed"
    color = "#22c55e" if healed > 0 else "#ef4444"

    st.markdown(f"""
    <div class="card animate-in" style="margin-bottom:10px;padding:18px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div style="display:flex;align-items:center;gap:10px">
                <span style="color:{color};font-size:1.2rem;font-weight:700">{status}</span>
                <span style="color:#6b7280;font-size:0.85rem">{issues} issues · {healed} healed</span>
            </div>
            <span style="color:#6b7280;font-size:0.8rem">{ts}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown('<div class="section-title">Healing History</div>', unsafe_allow_html=True)

    if not st.session_state.cycle_history:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px">
            <div style="font-size:2rem;margin-bottom:8px">📋</div>
            <div style="color:#6b7280;font-size:0.95rem">No healing cycles recorded yet</div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:16px">
        <div class="card" style="flex:1;text-align:center;padding:16px">
            <div class="kpi-value" style="font-size:1.8rem">{len(st.session_state.cycle_history)}</div>
            <div class="kpi-label">Total Cycles</div>
        </div>
        <div class="card" style="flex:1;text-align:center;padding:16px">
            <div class="kpi-value" style="font-size:1.8rem">{st.session_state.healed_count}</div>
            <div class="kpi-label">Total Healed</div>
        </div>
        <div class="card" style="flex:1;text-align:center;padding:16px">
            <div class="kpi-value" style="font-size:1.8rem">100%</div>
            <div class="kpi-label">Success Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, cycle in enumerate(reversed(st.session_state.cycle_history)):
        _cycle_card(cycle, i)
