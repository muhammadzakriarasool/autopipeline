"""Configuration — mode, scope, thresholds."""
import streamlit as st


def render():
    st.markdown('<div class="section-title">Configuration</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card animate-in" style="padding:24px">
            <div style="font-weight:600;color:#f0f0f3;margin-bottom:16px">🛡️ Operating Mode</div>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "Select mode",
            ["Shadow (Human Approval)", "Autonomous (Auto-Apply)", "Disabled"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card animate-in animate-in-delay-1" style="padding:24px;margin-top:16px">
            <div style="font-weight:600;color:#f0f0f3;margin-bottom:16px">📊 Detection Settings</div>
        """, unsafe_allow_html=True)

        polling = st.slider("Polling interval (seconds)", 60, 3600, 300, step=60)
        max_age = st.slider("Max freshness age (hours)", 1, 72, 24)
        vol_threshold = st.slider("Volume deviation threshold (%)", 5, 50, 20)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card animate-in animate-in-delay-2" style="padding:24px">
            <div style="font-weight:600;color:#f0f0f3;margin-bottom:16px">🎯 Scope</div>
        """, unsafe_allow_html=True)

        platforms = st.multiselect(
            "Platforms",
            ["dbt", "snowflake", "bigquery", "redshift", "databricks"],
            default=["dbt"],
        )
        domains = st.text_input("Domains (comma-separated)", placeholder="e.g. healthcare, finance")
        exclude = st.text_area(
            "Exclude URNs (one per line)",
            height=80,
            placeholder="urn:li:dataset:...",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card animate-in animate-in-delay-3" style="padding:24px;margin-top:16px">
            <div style="font-weight:600;color:#f0f0f3;margin-bottom:16px">🔗 Connection</div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <span class="pulse-dot green"></span>
                <span style="color:#22c55e;font-size:0.9rem">DataHub Connected</span>
            </div>
            <div style="color:#6b7280;font-size:0.85rem">
                Server: http://172.17.0.1:8080<br>
                Datasets: 1,113 accessible
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("💾 Save Configuration", type="primary", use_container_width=True):
        st.success("Configuration saved.")
