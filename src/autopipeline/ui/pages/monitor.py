"""Monitor — Live issue feed with actions."""
import streamlit as st


def _issue_row(issue: dict, idx: int):
    sev = issue.get("severity", "info")
    dot = "err" if sev == "critical" else "warn" if sev == "warning" else "live"

    st.markdown(f"""
    <div class="glass-card anim-fade-up" style="margin-bottom:8px;padding:18px">
        <div style="display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:10px">
                <span class="status-indicator {dot}"></span>
                <span style="font-weight:500;color:var(--text-primary);font-size:0.9rem">{issue['dataset']}</span>
            </div>
            <span style="color:var(--text-tertiary);font-size:0.75rem">{issue.get('detected_at', '')[:16]}</span>
        </div>
        <div style="margin-top:8px;color:var(--text-secondary);font-size:0.85rem;padding-left:16px">
            {issue.get('type', '')} — {issue.get('description', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if st.button("Diagnose", key=f"d_{idx}", use_container_width=True):
            st.session_state[f"diag_{idx}"] = True
            st.rerun()
    with c2:
        if st.button("Fix", key=f"f_{idx}", use_container_width=True, type="primary"):
            st.session_state.healed_count += 1
            st.session_state.issues.pop(idx)
            st.rerun()

    if st.session_state.get(f"diag_{idx}"):
        st.markdown("""
        <div class="glass-card" style="border-left:2px solid var(--accent);margin-bottom:8px;padding:14px 18px">
            <div style="font-size:0.85rem;color:var(--text-secondary)">
                <span style="color:var(--text-primary);font-weight:500">Root Cause:</span> Upstream source stale 48h<br>
                <span style="color:var(--text-primary);font-weight:500">Confidence:</span> 85%<br>
                <span style="color:var(--text-primary);font-weight:500">Fix:</span> assertion_update
            </div>
        </div>
        """, unsafe_allow_html=True)


def render():
    st.markdown('<div class="section-header">Active Issues</div>', unsafe_allow_html=True)

    if not st.session_state.issues:
        st.markdown("""
        <div class="glass-card empty-state">
            <div class="empty-state-icon">✅</div>
            <div class="empty-state-text" style="color:var(--success)">All Clear</div>
            <div class="empty-state-sub">No active issues detected</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, issue in enumerate(st.session_state.issues):
        _issue_row(issue, i)
