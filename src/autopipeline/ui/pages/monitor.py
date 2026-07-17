"""Live monitoring — issue feed with diagnose/fix actions."""
import streamlit as st


def _issue_card(issue: dict, index: int):
    severity_colors = {"critical": "red", "warning": "yellow", "info": "green"}
    dot_cls = severity_colors.get(issue.get("severity", "info"), "green")

    st.markdown(f"""
    <div class="card animate-in" style="margin-bottom:12px;padding:20px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <span class="pulse-dot {dot_cls}"></span>
                <span style="font-weight:600;color:#f0f0f3">{issue['dataset']}</span>
            </div>
            <span style="font-size:0.75rem;color:#6b7280">{issue.get('detected_at', '')}</span>
        </div>
        <div style="margin-top:8px;color:#a1a1aa;font-size:0.9rem">
            {issue.get('type', 'unknown')} — {issue.get('description', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔍 Diagnose", key=f"diag_{index}", use_container_width=True):
            st.session_state[f"diagnosed_{index}"] = True
            st.rerun()
    with c2:
        if st.button("🔧 Fix", key=f"fix_{index}", use_container_width=True, type="primary"):
            st.session_state.healed_count += 1
            st.session_state.issues.pop(index)
            st.rerun()

    if st.session_state.get(f"diagnosed_{index}"):
        st.markdown("""
        <div class="card" style="border-left:3px solid #6366f1;margin-bottom:12px;padding:16px">
            <div style="font-size:0.85rem;color:#a1a1aa">
                <b style="color:#f0f0f3">Root Cause:</b> Upstream source stale for 48h<br>
                <b style="color:#f0f0f3">Confidence:</b> 85%<br>
                <b style="color:#f0f0f3">Suggested Fix:</b> assertion_update
            </div>
        </div>
        """, unsafe_allow_html=True)


def render():
    st.markdown('<div class="section-title">Active Issues</div>', unsafe_allow_html=True)

    if not st.session_state.issues:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px">
            <div style="font-size:2rem;margin-bottom:8px">✅</div>
            <div style="color:#22c55e;font-weight:600;font-size:1.1rem">All Clear</div>
            <div style="color:#6b7280;font-size:0.9rem;margin-top:4px">No active issues detected</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, issue in enumerate(st.session_state.issues):
        _issue_card(issue, i)
