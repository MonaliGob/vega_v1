import streamlit as st
from utils.auth import check_password

def main():
    st.set_page_config(
        page_title="VEGA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
        <style>
        :root {
            --primary: #6200ee;
            --primary-variant: #3700b3;
            --secondary: #03dac6;
            --background: #121212;
            --surface: #1e1e1e;
            --error: #cf6679;
            --white: #ffffff;
        }
        .stApp {
            background-color: var(--background);
        }
        .material-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: var(--surface);
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
            color: var(--white);
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
        .material-card {
            background-color: var(--surface);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.2),
                       0px 1px 1px 0px rgba(0,0,0,0.14),
                       0px 1px 3px 0px rgba(0,0,0,0.12);
        }
        .material-content {
            margin-top: 88px;
            padding: 24px;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Roboto', sans-serif;
            color: var(--white);
            margin-bottom: 16px;
        }
        p {
            font-family: 'Roboto', sans-serif;
            color: rgba(255, 255, 255, 0.87);
            line-height: 1.5;
        }
        .metric-label {
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.6);
        }
        .metric-value {
            font-family: 'Roboto', sans-serif;
            font-size: 34px;
            font-weight: 400;
            color: var(--white);
        }
        </style>
    """, unsafe_allow_html=True)

    if not check_password():
        return

    st.markdown("""
        <div class="material-navbar">
            <div class="material-nav-content">
                <div class="material-nav-brand">
                    <img src="attached_assets/image_1739823857967.png" class="material-nav-logo">
                </div>
                <div class="material-nav-links">
                    <a href="/" class="material-nav-link">📊 Main</a>
                    <a href="/pages/database_config" class="material-nav-link">🔌 Databases</a>
                    <a href="/pages/execute_rules" class="material-nav-link">🎯 Execute Rules</a>
                    <a href="/pages/rule_config" class="material-nav-link">⚙️ Rules</a>
                    <a href="/pages/results" class="material-nav-link">📈 Results</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="material-content">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="material-card">
            <h2>System Overview</h2>
            <p>
            Welcome to VEGA - Your Enterprise Data Quality Guardian. This platform allows you to:
            <ul>
                <li>Connect to multiple databases</li>
                <li>Configure data quality rules</li>
                <li>Monitor data quality metrics</li>
                <li>Visualize results and trends</li>
            </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="material-card">
            <h2>Quick Stats</h2>
        </div>
        """, unsafe_allow_html=True)

        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        with metrics_col1:
            st.metric(label="Active Rules", value="12")
        with metrics_col2:
            st.metric(label="Checks Today", value="145")
        with metrics_col3:
            st.metric(label="Success Rate", value="98%")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()