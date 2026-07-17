"""Config — Mode, scope, thresholds."""
import streamlit as st


def render():
    st.markdown('<div class="section-header">Configuration</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="glass-card anim-fade-up" style="padding:20px">
            <div style="font-weight:500;color:var(--text-primary);font-size:0.9rem;margin-bottom:14px">Operating Mode</div>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "Mode",
            ["Shadow (Human Approval)", "Autonomous (Auto-Apply)", "Disabled"],
            label_visibility="collapsed",
            key="mode_radio",
        )

        st.markdown("""
        <div class="glass-card anim-fade-up delay-1" style="padding:20px;margin-top:12px">
            <div style="font-weight:500;color:var(--text-primary);font-size:0.9rem;margin-bottom:14px">Detection</div>
        </div>
        """, unsafe_allow_html=True)

        st.slider("Polling interval (s)", 60, 3600, 300, step=60, key="polling")
        st.slider("Max freshness age (h)", 1, 72, 24, key="max_age")
        st.slider("Volume deviation (%)", 5, 50, 20, key="vol_thresh")

    with c2:
        st.markdown("""
        <div class="glass-card anim-fade-up delay-2" style="padding:20px">
            <div style="font-weight:500;color:var(--text-primary);font-size:0.9rem;margin-bottom:14px">Scope</div>
        </div>
        """, unsafe_allow_html=True)

        st.multiselect(
            "Platforms",
            ["dbt", "snowflake", "bigquery", "redshift", "databricks"],
            default=["dbt"],
            key="platforms",
        )
        st.text_input("Domains", placeholder="healthcare, finance", key="domains")

        st.markdown("""
        <div class="glass-card anim-fade-up delay-3" style="padding:20px;margin-top:12px">
            <div style="font-weight:500;color:var(--text-primary);font-size:0.9rem;margin-bottom:14px">Connection</div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <span class="status-indicator live"></span>
                <span style="color:var(--success);font-size:0.85rem;font-weight:500">DataHub Connected</span>
            </div>
            <div style="color:var(--text-tertiary);font-size:0.8rem;line-height:1.6">
                Server: 172.17.0.1:8080<br>
                Datasets: 1,113 accessible
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Save Configuration", type="primary", use_container_width=True):
        st.success("Configuration saved.")
