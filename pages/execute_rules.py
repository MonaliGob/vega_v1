import streamlit as st
from utils.database import DatabaseConnector
from utils.data_quality import DataQualityChecker
import pandas as pd
import plotly.express as px

def app():
    st.title("Rule Execution")

    # Initialize database connector
    db_connector = DatabaseConnector()

    # Get all existing rules
    rules = db_connector.get_rules()

    if not rules:
        st.warning("No rules configured yet. Please add rules in the Rule Configuration page.")
        return

    # Rule selection
    selected_rules = st.multiselect(
        "Select Rules to Execute",
        options=[rule.name for rule in rules],
        default=[rule.name for rule in rules]
    )

    if st.button("Execute Selected Rules"):
        if not selected_rules:
            st.error("Please select at least one rule to execute")
            return

        st.write("Executing rules...")
        progress_bar = st.progress(0)

        # Filter selected rules
        rules_to_execute = [rule for rule in rules if rule.name in selected_rules]
        results = []

        for i, rule in enumerate(rules_to_execute):
            # Execute rule
            result = DataQualityChecker.execute_rule(db_connector.engine, {
                "id": rule.id,
                "name": rule.name,
                "type": rule.type,
                "table": rule.table,
                "column": rule.column,
                "parameters": rule.parameters
            })

            # Display rule execution details
            with st.expander(f"Rule Details: {rule.name}", expanded=True):
                st.write("Rule Configuration:")
                st.json({
                    "type": rule.type,
                    "table": rule.table,
                    "column": rule.column,
                    "parameters": rule.parameters
                })

                # Display the SQL query
                st.subheader("SQL Query")
                st.code(result['query'], language="sql")

                st.write(f"Score: {result['score']:.1f}%")
                if result['status'] == 'Failed':
                    st.error(f"Error: {result.get('error', 'Unknown error')}")

            results.append(result)
            progress_bar.progress((i + 1) / len(rules_to_execute))

        # Display results
        if results:
            st.success("Rules execution completed!")

            # Create results dataframe
            results_df = pd.DataFrame(results)

            # Visualization
            col1, col2 = st.columns([2, 1])

            with col1:
                fig = px.bar(
                    results_df,
                    x='rule_name',
                    y='score',
                    color='status',
                    title="Data Quality Scores by Rule"
                )
                fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Threshold")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Summary statistics
                avg_score = results_df['score'].mean()
                pass_count = sum(1 for r in results if r['score'] >= 95)

                st.metric("Average Score", f"{avg_score:.1f}%")
                st.metric("Passing Rules", f"{pass_count}/{len(results)}")

            # Detailed results table
            st.subheader("Detailed Results")
            st.dataframe(
                results_df[['rule_name', 'score', 'status', 'error']]
                .rename(columns={
                    'rule_name': 'Rule Name',
                    'score': 'Score (%)',
                    'status': 'Status',
                    'error': 'Error'
                })
            )

            # Save results to database
            for result in results:
                db_connector.save_result(result)

if __name__ == "__main__":
    app()