import streamlit as st
from utils.database import DatabaseConnector
from utils.auth import require_auth
import json
from typing import Dict, List
import os

def get_folder_structure(rules: List) -> Dict[str, List]:
    """Organize rules into folder structure"""
    folders = {}
    for rule in rules:
        folder = rule.folder if rule.folder else "/"
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(rule)
    return folders

@require_auth
def app():
    st.title("Rule Configuration")

    # Initialize database connector
    db_connector = DatabaseConnector()

    # Get existing rules for editing
    rules = db_connector.get_rules()
    folders = get_folder_structure(rules)

    # Initialize session state
    if 'editing_rule' not in st.session_state:
        st.session_state.editing_rule = None
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'current_folder' not in st.session_state:
        st.session_state.current_folder = "/"

    # Folder Navigation
    st.sidebar.header("Folders")
    all_folders = list(folders.keys())
    if "/" not in all_folders:
        all_folders.append("/")

    # New folder creation
    new_folder = st.sidebar.text_input("New Folder Name")
    if new_folder:
        if new_folder not in all_folders and new_folder.strip():
            all_folders.append(new_folder)
            st.sidebar.success(f"Folder '{new_folder}' created!")

    # Folder selection
    selected_folder = st.sidebar.selectbox(
        "Select Folder",
        options=sorted(all_folders),
        index=all_folders.index(st.session_state.current_folder)
    )
    st.session_state.current_folder = selected_folder

    # Rule Configuration Form
    st.header("Create/Edit Rule")

    # If editing, pre-fill form with rule data
    editing_rule = st.session_state.editing_rule
    rule_id = None

    if editing_rule:
        rule_id = editing_rule.id
        default_name = editing_rule.name
        default_description = editing_rule.description
        default_folder = editing_rule.folder
        default_db_type = editing_rule.database
        default_table = editing_rule.table
        default_rule_type = editing_rule.type
        default_column = editing_rule.column
        default_threshold = editing_rule.threshold
        default_parameters = editing_rule.parameters
    else:
        default_name = ""
        default_description = ""
        default_folder = selected_folder
        default_db_type = None
        default_table = ""
        default_rule_type = "completeness"
        default_column = ""
        default_threshold = 95
        default_parameters = {}

    with st.form(key=f"rule_form_{st.session_state.form_key}"):
        # Basic Rule Information
        col1, col2 = st.columns(2)
        with col1:
            rule_name = st.text_input("Rule Name", value=default_name)
        with col2:
            folder = st.selectbox(
                "Folder",
                options=sorted(all_folders),
                index=all_folders.index(default_folder if default_folder in all_folders else selected_folder)
            )

        rule_description = st.text_area("Description", value=default_description)

        # Database Configuration
        col1, col2 = st.columns(2)
        with col1:
            db_type = st.selectbox(
                "Database Type",
                ["postgresql"],  # Simplified for now
                index=0
            )

        # Get available tables
        available_tables = db_connector.get_available_tables(1)  # Using default connection

        with col2:
            table_name = st.selectbox(
                "Table Name",
                options=[""] + available_tables,
                index=0 if not default_table else available_tables.index(default_table) + 1
            )

        # Get columns for selected table
        available_columns = []
        if table_name:
            available_columns = db_connector.get_column_names(1, table_name)

        # Rule Type and Parameters
        rule_type = st.selectbox(
            "Rule Type",
            ["completeness", "uniqueness", "range"],
            index=["completeness", "uniqueness", "range"].index(default_rule_type)
        )

        column_name = st.selectbox(
            "Column Name",
            options=[""] + available_columns,
            index=0 if not default_column else (available_columns.index(default_column) + 1 if default_column in available_columns else 0)
        )

        # Conditional parameters based on rule type
        parameters = {}
        if rule_type == "range":
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input(
                    "Minimum Value",
                    value=float(default_parameters.get('min_val', 0.0))
                )
            with col2:
                max_val = st.number_input(
                    "Maximum Value",
                    value=float(default_parameters.get('max_val', 100.0))
                )
            parameters = {"min_val": min_val, "max_val": max_val}

        # Threshold Configuration
        threshold = st.slider(
            "Quality Threshold (%)",
            0, 100,
            value=int(default_threshold)
        )

        # Submit button
        button_label = "Update Rule" if editing_rule else "Create Rule"
        submit_button = st.form_submit_button(button_label)

        if submit_button:
            if not all([rule_name, table_name, column_name]):
                st.error("Please fill in all required fields")
            else:
                rule_config = {
                    "name": rule_name,
                    "description": rule_description,
                    "folder": folder,
                    "database": db_type,
                    "table": table_name,
                    "type": rule_type,
                    "column": column_name,
                    "threshold": threshold,
                    "parameters": parameters
                }

                if editing_rule:
                    rule_config["id"] = rule_id
                    db_connector.update_rule(rule_config)
                    st.success("Rule updated successfully!")
                    st.session_state.editing_rule = None
                    st.session_state.form_key += 1
                else:
                    db_connector.save_rule(rule_config)
                    st.success("Rule created successfully!")
                    st.session_state.form_key += 1

    # Cancel editing button
    if editing_rule:
        if st.button("Cancel Editing"):
            st.session_state.editing_rule = None
            st.session_state.form_key += 1
            st.experimental_rerun()

    # Display Rules in Current Folder
    st.header(f"Rules in {selected_folder}")

    current_folder_rules = folders.get(selected_folder, [])

    for rule in current_folder_rules:
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                with st.expander(f"Rule: {rule.name}"):
                    st.json({
                        "name": rule.name,
                        "description": rule.description,
                        "folder": rule.folder,
                        "database": rule.database,
                        "table": rule.table,
                        "type": rule.type,
                        "column": rule.column,
                        "threshold": rule.threshold,
                        "parameters": rule.parameters
                    })

            with col2:
                if st.button("Edit", key=f"edit_{rule.id}_{st.session_state.form_key}"):
                    st.session_state.editing_rule = rule
                    st.session_state.form_key += 1
                    st.experimental_rerun()

if __name__ == "__main__":
    app()