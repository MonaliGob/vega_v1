import os
import streamlit as st
from streamlit_navigation_bar import st_navbar
from utils.auth import check_password

def main():
    st.set_page_config(
        page_title="VEGA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    if not check_password():
        return

    pages = ["Main", "Execute Rules", "Rules", "Results"]
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(parent_dir, "assets/vega_logo.svg")
    styles = {
        "nav": {
            "background-color": "#6200ee",
            "justify-content": "center",
            "display": "flex",
            "align-items": "center",
            "padding": "0 24px",
            "width": "100%"
        },
        "img": {
            "padding-right": "14px",
            "height": "40px",
            "margin": "8px 0"
        },
        "span": {
            "color": "white",
            "padding": "14px",
            "display": "inline-block"
        },
        "active": {
            "background-color": "rgba(255, 255, 255, 0.1)",
            "color": "white",
            "font-weight": "500",
            "padding": "14px",
            "border-radius": "4px"
        }
    }
    options = {
        "show_menu": False,
        "show_sidebar": False,
    }

    page = st_navbar(
        pages,
        logo_path=logo_path,
        styles=styles,
        options=options,
    )

    # Logo Section
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo_path, use_container_width=True)

    # Overview Section
    st.markdown('<div class="md-card">', unsafe_allow_html=True)
    st.header("System Overview")

    # Stats Row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">98%</div>
                <div class="stat-label">Data Quality Score</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">145</div>
                <div class="stat-label">Active Rules</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">24/7</div>
                <div class="stat-label">Monitoring</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Features Section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="md-card">', unsafe_allow_html=True)
        st.subheader("🎯 Key Features")
        st.markdown("""
        - Database-native rule execution
        - Advanced multi-rule selection
        - Real-time monitoring capabilities
        - Enhanced configuration interface
        - Comprehensive reporting
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="md-card">', unsafe_allow_html=True)
        st.subheader("📈 Quick Actions")
        if st.button("Execute Rules"):
            st.switch_page("pages/execute_rules.py")
        if st.button("Configure Rules"):
            st.switch_page("pages/rule_config.py")
        if st.button("View Results"):
            st.switch_page("pages/results.py")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()