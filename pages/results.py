import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.database import DatabaseConnector
from utils.auth import require_auth
import pandas as pd
import numpy as np

@require_auth
def app():
    st.set_page_config(
        page_title="VEGA - Results",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Material Design inspired CSS
    st.markdown("""
        <style>
        /* Material Design Colors and Base Styles */
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

        /* Material Design Navigation */
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

        /* Material Design Cards */
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

        /* Material Design Typography */
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
        </style>
    """, unsafe_allow_html=True)

    # Material Design Navigation Bar
    st.markdown("""
        <div class="material-navbar">
            <div class="material-nav-content">
                <div class="material-nav-brand">
                    <img src="../attached_assets/image_1739823857967.png" class="material-nav-logo">
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

    st.title("Quality Check Results")

    # Initialize database connector
    db_connector = DatabaseConnector()

    # Get all rules and their results
    rules = db_connector.get_rules()
    results = db_connector.get_results()

    if not rules:
        st.warning("No rules have been configured yet. Please add rules in the Rule Configuration page.")
        return

    if not results:
        st.info("No quality checks have been executed yet. Run some checks in the Rule Execution page.")
        return

    # Create results DataFrame
    results_data = []
    for result in results:
        rule = next((r for r in rules if r.id == result.rule_id), None)
        if rule:
            results_data.append({
                'rule_id': rule.id,
                'rule_name': rule.name,
                'rule_type': rule.type,
                'status': result.status,
                'score': result.score,
                'error': result.error,
                'executed_at': result.executed_at,
                'table': rule.table,
                'column': rule.column
            })

    results_df = pd.DataFrame(results_data)
    results_df = results_df.sort_values('executed_at', ascending=False)

    # Multi-select rules for analysis
    st.markdown('<div class="material-card">', unsafe_allow_html=True)
    selected_rule_names = st.multiselect(
        "Select Rules to Analyze",
        options=sorted([rule.name for rule in rules]),
        default=sorted([rule.name for rule in rules])[:3]
    )

    if selected_rule_names:
        latest_results = (results_df[results_df['rule_name'].isin(selected_rule_names)]
                         .sort_values('executed_at')
                         .groupby('rule_name')
                         .last()
                         .reset_index())

        if not latest_results.empty:
            # Combined statistics in PowerBI style
            col1, col2 = st.columns(2)

            with col1:
                pass_threshold = 95
                pass_count = sum(latest_results['score'] >= pass_threshold)
                fail_count = len(latest_results) - pass_count

                pie_data = pd.DataFrame([
                    {'status': 'Passing', 'count': pass_count},
                    {'status': 'Failing', 'count': fail_count}
                ])

                fig_pie = px.pie(
                    pie_data,
                    values='count',
                    names='status',
                    title=f"Rules Pass/Fail Distribution (Threshold: {pass_threshold}%)",
                    color='status',
                    color_discrete_map={'Passing': '#00B8D4', 'Failing': '#FF5252'},
                    template="plotly_dark"
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                fig_trend = go.Figure()
                for rule_name in selected_rule_names:
                    rule_data = results_df[results_df['rule_name'] == rule_name]
                    fig_trend.add_trace(go.Scatter(
                        x=rule_data['executed_at'],
                        y=rule_data['score'],
                        name=rule_name,
                        mode='lines+markers',
                        line=dict(width=2),
                        marker=dict(size=8)
                    ))

                fig_trend.update_layout(
                    title="Score History for Selected Rules",
                    xaxis_title="Execution Time",
                    yaxis_title="Score (%)",
                    hovermode="x unified",
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                fig_trend.add_hline(y=95, line_dash="dash", line_color="#FF5252",
                                      annotation_text="Threshold (95%)")
                st.plotly_chart(fig_trend, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = latest_results['score'].mean()
                st.metric("Average Score", f"{avg_score:.1f}%")
            with col2:
                pass_percentage = (pass_count / len(selected_rule_names)) * 100
                st.metric("Rules Passing", f"{pass_count}/{len(selected_rule_names)} ({pass_percentage:.1f}%)")
            with col3:
                total_checks = len(results_df[results_df['rule_name'].isin(selected_rule_names)])
                st.metric("Total Checks", total_checks)

    st.markdown('</div>', unsafe_allow_html=True)

    # Individual rule details
    for rule in rules:
        rule_results = results_df[results_df['rule_id'] == rule.id]
        if not rule_results.empty:
            latest_score = rule_results.iloc[0]['score']
            status = "✅" if latest_score >= 95 else "❌"

            st.markdown(f'<div class="material-card">', unsafe_allow_html=True)
            st.markdown(f"### Rule: {rule.name} {status} (Latest Score: {latest_score:.1f}%)")

            # Rule information
            st.markdown(f"""
            **Rule Details:**
            - Type: {rule.type}
            - Table: {rule.table}
            - Column: {rule.column}
            - Latest Check: {rule_results.iloc[0]['executed_at'].strftime('%Y-%m-%d %H:%M:%S')}
            """)

            # Line chart
            fig = px.line(
                rule_results,
                x='executed_at',
                y='score',
                title=f"Score History for {rule.name}",
                markers=True,
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, b=0, l=0, r=0)
            )
            fig.add_hline(y=rule.threshold, line_dash="dash", line_color="#FF5252",
                           annotation_text=f"Threshold ({rule.threshold}%)")
            st.plotly_chart(fig, use_container_width=True)

            # Results table
            st.dataframe(
                rule_results[['executed_at', 'score', 'status', 'error']]
                .rename(columns={
                    'executed_at': 'Execution Time',
                    'score': 'Score (%)',
                    'status': 'Status',
                    'error': 'Error'
                }),
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # closing content-container

if __name__ == "__main__":
    app()