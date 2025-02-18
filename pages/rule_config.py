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
    if 'expanded_folders' not in st.session_state:
        st.session_state.expanded_folders = {"/": True}
    if 'new_folder_name' not in st.session_state:
        st.session_state.new_folder_name = ""

    # Sidebar with Windows Explorer-like folder tree
    with st.sidebar:
        st.markdown("""
        <style>
        .folder-tree {
            margin-left: 10px;
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            padding-left: 10px;
        }
        .folder-item {
            padding: 5px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        .folder-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .folder-selected {
            background-color: rgba(98, 0, 238, 0.2);
        }
        /* Light blue folder icons */
        .stButton button {
            color: #87CEEB !important;
        }
        .stButton button:hover {
            color: #ADD8E6 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("### 📁 Folders")

        # New folder creation with button
        col1, col2 = st.columns([3, 1])
        with col1:
            new_folder_name = st.text_input("📝 New Folder", key="new_folder_input", value=st.session_state.new_folder_name)
        with col2:
            if st.button("Create", key="create_folder_btn"):
                if new_folder_name and new_folder_name.strip():
                    if new_folder_name not in folders:
                        folders[new_folder_name] = []
                        st.session_state.expanded_folders[new_folder_name] = True
                        st.success(f"📁 Folder '{new_folder_name}' created!")
                        st.session_state.new_folder_name = ""
                    else:
                        st.error("Folder already exists!")
                else:
                    st.error("Please enter a folder name!")

        # Display folder tree
        all_folders = sorted(list(set(list(folders.keys()) + ["/"])))

        def render_folder(folder, level=0):
            is_current = folder == st.session_state.current_folder
            folder_class = "folder-selected" if is_current else ""

            # Count rules in folder
            rule_count = len(folders.get(folder, []))

            # Create expandable section
            is_expanded = st.session_state.expanded_folders.get(folder, False)
            icon = "📂" if is_expanded else "📁"

            # Add folder button with proper indentation
            col1, col2 = st.columns([8, 2])
            with col1:
                if st.button(
                    f"{' ' * (level * 2)}{icon} {folder} ({rule_count})",
                    key=f"folder_{folder}",
                    help=f"Click to select folder: {folder}"
                ):
                    st.session_state.current_folder = folder
                    st.rerun()

            with col2:
                if st.button(
                    "👁️" if is_expanded else "👁️",
                    key=f"expand_{folder}",
                    help="Toggle folder view"
                ):
                    st.session_state.expanded_folders[folder] = not is_expanded
                    st.rerun()

        # Render root folder first
        render_folder("/")

        # Render all other folders
        for folder in [f for f in all_folders if f != "/"]:
            render_folder(folder, level=1)

    # Main content area
    selected_folder = st.session_state.current_folder

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
                ["postgresql"],  # Add more types as needed
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
            [
                "completeness",
                "uniqueness",
                "range",
                "pattern",
                "date_format",
                "cross_column",
                "statistical"
            ],
            index=["completeness", "uniqueness", "range", "pattern", "date_format", "cross_column", "statistical"].index(default_rule_type)
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

        elif rule_type == "pattern":
            pattern = st.text_input(
                "Regex Pattern",
                value=default_parameters.get('pattern', ''),
                help="Enter a regular expression pattern to validate the data"
            )
            parameters = {"pattern": pattern}

        elif rule_type == "date_format":
            format = st.selectbox(
                "Date Format",
                ["YYYY-MM-DD", "MM/DD/YYYY", "DD-MM-YYYY", "YYYY/MM/DD"],
                index=0
            )
            parameters = {"format": format}

        elif rule_type == "cross_column":
            col2 = st.selectbox(
                "Compare with Column",
                options=[""] + available_columns,
                index=0
            )
            operator = st.selectbox(
                "Comparison Operator",
                ["=", ">", "<", ">=", "<=", "!="],
                index=0
            )
            parameters = {"column2": col2, "operator": operator}

        elif rule_type == "statistical":
            method = st.selectbox(
                "Statistical Method",
                ["zscore"],
                index=0
            )
            threshold = st.number_input(
                "Z-Score Threshold",
                value=float(default_parameters.get('threshold', 3.0)),
                help="Data points beyond this z-score are considered outliers"
            )
            parameters = {"method": method, "threshold": threshold}

        # Threshold Configuration
        threshold = st.slider(
            "Quality Threshold (%)",
            0, 100,
            value=int(default_threshold)
        )

        # Submit button
        button_label = "Update Rule" if editing_rule else "Create Rule"
        submit = st.form_submit_button(button_label)

        if submit:
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
            st.rerun()

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
                    st.rerun()

if __name__ == "__main__":
    app()