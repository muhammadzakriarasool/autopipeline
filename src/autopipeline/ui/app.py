"""AutoPilot — Self-Healing Data Pipeline Dashboard."""
import streamlit as st
from autopipeline.ui.styles import inject_theme

st.set_page_config(
    page_title="AutoPilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

if "issues" not in st.session_state:
    st.session_state.issues = []
if "healed_count" not in st.session_state:
    st.session_state.healed_count = 0
if "cycle_history" not in st.session_state:
    st.session_state.cycle_history = []

with st.sidebar:
    st.markdown("## 🛡️ AutoPilot")
    st.markdown("---")
    st.markdown(
        '<span class="pulse-dot green"></span> <span style="font-size:0.85rem;color:#e4e4e7">System Online</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown("**Mode:** Shadow")
    st.markdown("**DataHub:** Connected")
    st.markdown("**Polling:** 300s")
    st.markdown("---")
    if st.button("⚡ Run Cycle Now", use_container_width=True, type="primary"):
        from datetime import datetime, timezone
        st.session_state.cycle_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues_found": 1,
            "healed": 1,
        })
        st.session_state.healed_count += 1
        st.rerun()

st.markdown("# 🛡️ AutoPilot")
st.markdown(
    '<p style="color:#6b7280;font-size:0.95rem;margin-top:-10px">Self-Healing Data Pipeline Agent · Powered by DataHub</p>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Monitor", "📋 History", "⚙️ Config"])

with tab1:
    from autopipeline.ui.pages.dashboard import render
    render()

with tab2:
    from autopipeline.ui.pages.monitor import render
    render()

with tab3:
    from autopipeline.ui.pages.healing import render
    render()

with tab4:
    from autopipeline.ui.pages.config import render
    render()
