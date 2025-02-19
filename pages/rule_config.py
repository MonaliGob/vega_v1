import streamlit as st
from utils.database import DatabaseConnector
from utils.auth import require_auth
from utils.data_quality import DataQualityChecker
import json
from typing import Dict, List
import os
from datetime import datetime
from st_dnd import DragAndDrop

def get_folder_structure(rules: List) -> Dict[str, List]:
    db_connector = DatabaseConnector()
    return db_connector.get_folder_structure()

def get_preview_sql(rule: Dict) -> str:
    """Generate preview SQL for a rule configuration"""
    try:
        if rule['type'] == 'completeness':
            return DataQualityChecker.generate_completeness_query(rule['table'], rule['column'])
        elif rule['type'] == 'uniqueness':
            return DataQualityChecker.generate_uniqueness_query(rule['table'], rule['column'])
        elif rule['type'] == 'range':
            params = rule.get('parameters', {})
            min_val = float(params.get('min_val', 0))
            max_val = float(params.get('max_val', 100))
            return DataQualityChecker.generate_range_query(rule['table'], rule['column'], min_val, max_val)
        elif rule['type'] == 'pattern':
            params = rule.get('parameters', {})
            pattern = params.get('pattern', '')
            return DataQualityChecker.generate_pattern_query(rule['table'], rule['column'], pattern)
        elif rule['type'] == 'date_format':
            params = rule.get('parameters', {})
            format = params.get('format', 'YYYY-MM-DD')
            return DataQualityChecker.generate_date_format_query(rule['table'], rule['column'], format)
        elif rule['type'] == 'cross_column':
            params = rule.get('parameters', {})
            column2 = params.get('column2', '')
            operator = params.get('operator', '=')
            value = params.get('value', None)
            return DataQualityChecker.generate_cross_column_query(rule['table'], rule['column'], column2, operator, value)
        elif rule['type'] == 'statistical':
            params = rule.get('parameters', {})
            method = params.get('method', 'zscore')
            threshold = float(params.get('threshold', 3.0))
            return DataQualityChecker.generate_statistical_query(rule['table'], rule['column'], method, threshold)
        return "Unsupported rule type"
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def handle_folder_drop(source_id: str, target_folder: str, db_connector: DatabaseConnector):
    """Handle dropping a folder or rule into a target folder"""
    try:
        if source_id.startswith('folder_'):
            # Moving a folder
            folder_name = source_id[7:]  # Remove 'folder_' prefix
            if folder_name != target_folder and not target_folder.startswith(folder_name):
                new_name = f"{target_folder}/{os.path.basename(folder_name)}" if target_folder != "/" else os.path.basename(folder_name)
                db_connector.rename_folder(folder_name, new_name)
                return True
        elif source_id.startswith('rule_'):
            # Moving a rule
            rule_id = int(source_id[5:])  # Remove 'rule_' prefix
            db_connector.move_rule(rule_id, target_folder)
            return True
        return False
    except Exception as e:
        st.error(f"Error moving item: {str(e)}")
        return False

@require_auth
def app():
    st.title("Rule Configuration")

    # Initialize database connector
    db_connector = DatabaseConnector()

    # Get existing rules and folder structure
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
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = ""
    if 'available_columns' not in st.session_state:
        st.session_state.available_columns = []

    # Get available tables
    available_tables = db_connector.get_available_tables(1)  # Using default connection

    # Table selection outside form to handle updates
    selected_table = st.selectbox(
        "Select Table",
        options=[""] + available_tables,
        index=0 if not st.session_state.selected_table else available_tables.index(st.session_state.selected_table) + 1
    )

    # Update columns when table changes
    if selected_table != st.session_state.selected_table:
        st.session_state.selected_table = selected_table
        if selected_table:
            st.session_state.available_columns = db_connector.get_column_names(1, selected_table)
        else:
            st.session_state.available_columns = []
        st.rerun()

    # Rule Configuration Form
    with st.form(key=f"rule_form_{st.session_state.form_key}"):
        st.header("Create/Edit Rule")

        # If editing, pre-fill form with rule data
        editing_rule = st.session_state.editing_rule
        rule_id = None

        if editing_rule:
            rule_id = editing_rule.id
            default_name = editing_rule.name
            default_description = editing_rule.description
            default_folder = editing_rule.folder
            default_rule_type = editing_rule.type
            default_column = editing_rule.column
            default_threshold = editing_rule.threshold
            default_parameters = editing_rule.parameters
        else:
            default_name = ""
            default_description = ""
            default_folder = "/"
            default_rule_type = "completeness"
            default_column = ""
            default_threshold = 95
            default_parameters = {}

        # Basic Rule Information
        col1, col2 = st.columns(2)
        with col1:
            rule_name = st.text_input("Rule Name", value=default_name)
        with col2:
            folder = st.selectbox(
                "Folder",
                options=sorted(list(folders.keys())),
                index=sorted(list(folders.keys())).index(default_folder if default_folder in folders else "/")
            )

        rule_description = st.text_area("Description", value=default_description)

        # Database Configuration section
        st.subheader("Database Configuration")

        # Display selected table (readonly in form)
        st.text_input("Selected Table", value=selected_table, disabled=True)

        # Column selection
        column_name = st.selectbox(
            "Column Name",
            options=[""] + st.session_state.available_columns,
            index=0 if not default_column else (st.session_state.available_columns.index(default_column) + 1 if default_column in st.session_state.available_columns else 0)
        )

        # Rule Type and Parameters
        st.subheader("Rule Configuration")
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
                options=[""] + st.session_state.available_columns,
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
        quality_threshold = st.slider(
            "Quality Threshold (%)",
            0, 100,
            value=int(default_threshold)
        )

        # Submit button
        submitted = st.form_submit_button("Save Rule")

        if submitted:
            if not all([rule_name, selected_table, column_name]):
                st.error("Please fill in all required fields")
            else:
                rule_config = {
                    "name": rule_name,
                    "description": rule_description,
                    "folder": folder,
                    "database": "postgresql",
                    "table": selected_table,
                    "type": rule_type,
                    "column": column_name,
                    "threshold": quality_threshold,
                    "parameters": parameters
                }

                try:
                    if editing_rule:
                        rule_config["id"] = rule_id
                        db_connector.update_rule(rule_config)
                        # Generate and show SQL preview
                        preview_sql = get_preview_sql(rule_config)
                        st.success("Rule updated successfully!")
                        with st.expander("View Effective SQL", expanded=True):
                            st.code(preview_sql, language="sql")
                        st.session_state.editing_rule = None
                    else:
                        db_connector.save_rule(rule_config)
                        # Generate and show SQL preview
                        preview_sql = get_preview_sql(rule_config)
                        st.success("Rule created successfully!")
                        with st.expander("View Effective SQL", expanded=True):
                            st.code(preview_sql, language="sql")

                    st.session_state.form_key += 1
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Cancel editing button
    if editing_rule:
        if st.button("Cancel Editing"):
            st.session_state.editing_rule = None
            st.session_state.form_key += 1
            st.rerun()

    # Sidebar with draggable folder tree
    with st.sidebar:
        st.markdown("""
            <style>
            .folder-tree {
                margin-left: 10px;
                border-left: 1px solid rgba(255, 255, 255, 0.1);
                padding-left: 10px;
            }
            .draggable-item {
                cursor: move;
                transition: background-color 0.2s;
                border-radius: 4px;
                padding: 8px;
                margin: 4px 0;
            }
            .draggable-item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .drop-target {
                border: 2px dashed rgba(98, 0, 238, 0.5);
                border-radius: 4px;
                padding: 8px;
                margin: 4px 0;
                transition: all 0.2s;
            }
            .drop-target.hover {
                border-color: rgba(98, 0, 238, 1);
                background-color: rgba(98, 0, 238, 0.1);
            }
            .folder-icon {
                color: #87CEEB;
                margin-right: 5px;
            }
            .rule-icon {
                color: #B0C4DE;
                margin-right: 5px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("### 📁 Folders")

        # Parent folder selection for new folders
        col1, col2 = st.columns([3, 1])
        with col1:
            parent_folder = st.selectbox(
                "Parent Folder",
                options=["/"] + sorted([f for f in folders.keys() if f != "/"]),
                key="parent_folder_select"
            )
            new_folder_name = st.text_input(
                "📝 New Folder",
                key="new_folder_input",
                value=st.session_state.new_folder_name
            )
        with col2:
            if st.button("Create", key="create_folder_btn"):
                if new_folder_name and new_folder_name.strip():
                    try:
                        full_folder_path = (
                            f"{parent_folder}/{new_folder_name}"
                            if parent_folder != "/"
                            else new_folder_name
                        )

                        if not db_connector.folder_exists(full_folder_path):
                            db_connector.create_folder({
                                "name": full_folder_path,
                                "description": f"Created on {datetime.utcnow()}",
                                "parent_folder": parent_folder
                            })
                            st.session_state.expanded_folders[full_folder_path] = True
                            st.success(f"📁 Folder '{full_folder_path}' created!")
                            st.session_state.new_folder_name = ""
                            st.rerun()
                        else:
                            st.error("Folder already exists!")
                    except Exception as e:
                        st.error(f"Failed to create folder: {str(e)}")
                else:
                    st.error("Please enter a folder name!")

        # Display folder tree with drag and drop
        def render_folder(folder: str, level: int = 0):
            is_expanded = st.session_state.expanded_folders.get(folder, False)

            # Create draggable folder item
            folder_id = f"folder_{folder}"
            with DragAndDrop(key=folder_id, type="folder"):
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.markdown(
                        f"""
                        <div class="draggable-item" style="margin-left: {level * 20}px">
                            {'📂' if is_expanded else '📁'} {folder}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col2:
                    if st.button("👁️", key=f"expand_{folder}"):
                        st.session_state.expanded_folders[folder] = not is_expanded
                        st.rerun()

            # Create drop target zone
            with DragAndDrop(key=f"drop_{folder}", type="folder", on_drop=lambda src: handle_folder_drop(src, folder, db_connector)):
                st.markdown(
                    f"""<div class="drop-target" style="margin-left: {level * 20}px">
                        Drop here to move to {folder}
                    </div>""",
                    unsafe_allow_html=True
                )

            if is_expanded:
                # Display rules in folder
                for rule in folders.get(folder, []):
                    rule_id = f"rule_{rule.id}"
                    with DragAndDrop(key=rule_id, type="rule"):
                        st.markdown(
                            f"""
                            <div class="draggable-item" style="margin-left: {(level + 1) * 20}px">
                                📄 {rule.name}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # Display child folders
                child_folders = [f for f in folders.keys() if f != "/" and f.startswith(folder + "/")]
                for child in sorted(child_folders):
                    render_folder(child, level + 1)

        # Render root folder
        render_folder("/")

        # Render top-level folders
        for folder in [f for f in folders.keys() if f != "/" and "/" not in f[1:]]:
            render_folder(folder, 1)

    # Display Rules in Current Folder
    st.header(f"Rules in {st.session_state.current_folder}")

    current_folder_rules = folders.get(st.session_state.current_folder, [])

    for rule in current_folder_rules:
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                with st.expander(f"Rule: {rule.name}"):
                    # Rule configuration
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

                    # Display SQL preview
                    st.markdown("### Effective SQL")
                    preview_sql = get_preview_sql({
                        "type": rule.type,
                        "table": rule.table,
                        "column": rule.column,
                        "parameters": rule.parameters
                    })
                    st.code(preview_sql, language="sql")

            with col2:
                if st.button("Edit", key=f"edit_{rule.id}_{st.session_state.form_key}"):
                    st.session_state.editing_rule = rule
                    st.session_state.form_key += 1
                    st.rerun()

if __name__ == "__main__":
    app()