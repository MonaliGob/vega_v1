import streamlit as st
from utils.database import DatabaseConnector
import json

def app():
    st.title("Database Connection Management")

    # Initialize database connector
    db_connector = DatabaseConnector()

    # Initialize session state for editing
    if 'editing_connection' not in st.session_state:
        st.session_state.editing_connection = None
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0

    # Get existing connections
    connections = db_connector.get_database_connections()

    # Connection Configuration Form
    st.header("Create/Edit Database Connection")

    # If editing, pre-fill form with connection data
    editing_connection = st.session_state.editing_connection
    connection_id = None

    if editing_connection:
        connection_id = editing_connection.id
        default_name = editing_connection.name
        default_description = editing_connection.description
        default_type = editing_connection.connection_type
        default_host = editing_connection.host
        default_port = editing_connection.port
        default_database = editing_connection.database
        default_username = editing_connection.username
        default_ssl_mode = editing_connection.ssl_mode
    else:
        default_name = ""
        default_description = ""
        default_type = "postgresql"
        default_host = ""
        default_port = 5432
        default_database = ""
        default_username = ""
        default_ssl_mode = "require"

    with st.form(key=f"connection_form_{st.session_state.form_key}"):
        # Basic Connection Information
        name = st.text_input("Connection Name", value=default_name)
        description = st.text_area("Description", value=default_description)

        # Connection Details
        col1, col2 = st.columns(2)
        with col1:
            conn_type = st.selectbox(
                "Database Type",
                ["postgresql", "mysql"],  # Add more types as needed
                index=0 if default_type == "postgresql" else 1
            )
            host = st.text_input("Host", value=default_host)
            port = st.number_input("Port", value=default_port)

        with col2:
            database = st.text_input("Database Name", value=default_database)
            username = st.text_input("Username", value=default_username)
            password = st.text_input("Password", type="password")

        # Advanced Options
        with st.expander("Advanced Options"):
            ssl_mode = st.selectbox(
                "SSL Mode",
                ["require", "verify-full", "verify-ca", "disable"],
                index=0 if default_ssl_mode == "require" else 3
            )

        # Test Connection Button
        test_conn = st.form_submit_button("Test Connection")
        if test_conn:
            success = db_connector.test_connection({
                "connection_type": conn_type,
                "host": host,
                "port": port,
                "database": database,
                "username": username,
                "password": password,
                "ssl_mode": ssl_mode
            })
            if success:
                st.success("Connection test successful!")
            else:
                st.error("Connection test failed. Please check your settings.")

        # Submit button
        button_label = "Update Connection" if editing_connection else "Create Connection"
        submit = st.form_submit_button(button_label)

        if submit:
            if not all([name, host, port, database, username]):
                st.error("Please fill in all required fields")
            else:
                connection_config = {
                    "name": name,
                    "description": description,
                    "connection_type": conn_type,
                    "host": host,
                    "port": port,
                    "database": database,
                    "username": username,
                    "ssl_mode": ssl_mode
                }
                
                if password:  # Only update password if provided
                    connection_config["password"] = password

                if editing_connection:
                    connection_config["id"] = connection_id
                    success = db_connector.update_database_connection(connection_config)
                    if success:
                        st.success("Connection updated successfully!")
                        st.session_state.editing_connection = None
                        st.session_state.form_key += 1
                else:
                    success = db_connector.save_database_connection(connection_config)
                    if success:
                        st.success("Connection created successfully!")
                        st.session_state.form_key += 1

    # Cancel editing button
    if editing_connection:
        if st.button("Cancel Editing"):
            st.session_state.editing_connection = None
            st.session_state.form_key += 1
            st.experimental_rerun()

    # Display Existing Connections
    st.header("Existing Connections")
    
    for conn in connections:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                with st.expander(f"Connection: {conn.name}"):
                    st.json({
                        "name": conn.name,
                        "description": conn.description,
                        "type": conn.connection_type,
                        "host": conn.host,
                        "port": conn.port,
                        "database": conn.database,
                        "username": conn.username,
                        "ssl_mode": conn.ssl_mode,
                        "last_connected": conn.last_connected_at.strftime("%Y-%m-%d %H:%M:%S") if conn.last_connected_at else "Never"
                    })

            with col2:
                if st.button("Test", key=f"test_{conn.id}"):
                    success = db_connector.test_connection({
                        "id": conn.id
                    })
                    if success:
                        st.success("Connection test successful!")
                    else:
                        st.error("Connection test failed.")

            with col3:
                if st.button("Edit", key=f"edit_{conn.id}_{st.session_state.form_key}"):
                    st.session_state.editing_connection = conn
                    st.session_state.form_key += 1
                    st.experimental_rerun()

if __name__ == "__main__":
    app()
