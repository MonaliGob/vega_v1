import streamlit as st
from utils.auth import check_password

def main():
    st.set_page_config(
        page_title="VEGA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
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

        /* Logo Container */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 2rem auto;
            padding: 2rem;
            max-width: 300px;
            background: var(--md-sys-color-surface);
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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

        /* Material Design Navigation */
        .material-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: var(--md-sys-color-surface);
            padding: 8px 16px;
            z-index: 1000;
            box-shadow: 0px 2px 4px -1px rgba(0,0,0,0.2), 
                       0px 4px 5px 0px rgba(0,0,0,0.14), 
                       0px 1px 10px 0px rgba(0,0,0,0.12);
        }

        .material-nav-content {
            display: flex;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            height: 64px;
        }

        .material-nav-brand {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .material-nav-logo {
            height: 40px;
        }

        .material-nav-links {
            display: flex;
            align-items: center;
            margin-left: 48px;
            gap: 24px;
        }

        .material-nav-link {
            color: var(--md-sys-color-on-primary);
            text-decoration: none;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.1px;
            text-transform: uppercase;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }

        .material-nav-link:hover {
            background-color: rgba(255, 255, 255, 0.08);
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
        </style>
    """, unsafe_allow_html=True)

    if not check_password():
        return

    # Material Design Navigation Bar
    st.markdown("""
        <div class="material-navbar">
            <div class="material-nav-content">
                <div class="material-nav-brand">
                    <img src="attached_assets/image_1739823857967.png" class="material-nav-logo">
                </div>
                <div class="material-nav-links">
                    <a href="/" class="material-nav-link">📊 Main</a>
                    <a href="/pages/execute_rules" class="material-nav-link">🎯 Execute Rules</a>
                    <a href="/pages/rule_config" class="material-nav-link">⚙️ Rules</a>
                    <a href="/pages/results" class="material-nav-link">📈 Results</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Content wrapper with Material Design spacing
    st.markdown('<div class="material-content">', unsafe_allow_html=True)

    # Logo Section
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("attached_assets/image_1739823857967.png", use_container_width=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()