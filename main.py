import streamlit as st
from utils.auth import check_password

def main():
    st.set_page_config(
        page_title="VEGA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Material Design inspired CSS
    st.markdown("""
        <style>
        /* Base Theme */
        :root {
            --md-sys-color-primary: #6200ee;
            --md-sys-color-surface: #1e1e1e;
            --md-sys-color-background: #121212;
            --md-sys-color-error: #cf6679;
            --md-sys-color-on-primary: #ffffff;
            --md-sys-color-on-surface: rgba(255, 255, 255, 0.87);
            --md-sys-color-on-background: rgba(255, 255, 255, 0.87);
            --md-sys-color-surface-variant: #373737;
        }

        /* Global Styles */
        .stApp {
            background-color: var(--md-sys-color-background);
        }

        /* Material Design Components */
        .md-card {
            background-color: var(--md-sys-color-surface);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2);
            transition: box-shadow 0.3s ease-in-out;
        }

        .md-card:hover {
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.3);
        }

        /* Typography */
        h1, h2, h3 {
            color: var(--md-sys-color-on-background);
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            letter-spacing: 0.0125em;
            margin-bottom: 16px;
        }

        h1 {
            font-size: 2.125rem;
            line-height: 2.5rem;
        }

        h2 {
            font-size: 1.5rem;
            line-height: 2rem;
        }

        p {
            color: var(--md-sys-color-on-surface);
            font-family: 'Roboto', sans-serif;
            font-size: 1rem;
            line-height: 1.5rem;
            letter-spacing: 0.03125em;
        }

        /* Custom Components */
        .stat-card {
            background-color: var(--md-sys-color-surface-variant);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 500;
            color: var(--md-sys-color-on-background);
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface);
            margin-top: 4px;
        }

        /* Streamlit Overrides */
        .stButton button {
            background-color: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            transition: background-color 0.2s ease;
        }

        .stButton button:hover {
            background-color: #7722FF;
            border: none;
        }

        .stTextInput input, .stSelectbox select {
            background-color: var(--md-sys-color-surface-variant);
            color: var(--md-sys-color-on-surface);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 4px;
        }

        /* Navigation */
        .stSidebar {
            background-color: var(--md-sys-color-surface);
        }
        </style>
    """, unsafe_allow_html=True)

    if not check_password():
        return

    # Main Content
    st.title("VEGA - Data Quality Platform")

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