import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from .models import get_db, Rule, Result, DatabaseConnection, Folder, engine
import os
import psycopg2
from psycopg2 import sql
from datetime import datetime

class DatabaseConnector:
    def __init__(self):
        self.db = next(get_db())
        self.engine = engine

    def get_database_connections(self) -> List[DatabaseConnection]:
        """Get all database connections"""
        return self.db.query(DatabaseConnection).all()

    def save_database_connection(self, connection_data: Dict) -> bool:
        """Save a new database connection"""
        try:
            connection = DatabaseConnection(
                name=connection_data["name"],
                description=connection_data.get("description", ""),
                connection_type=connection_data["connection_type"],
                host=connection_data["host"],
                port=connection_data["port"],
                database=connection_data["database"],
                username=connection_data["username"],
                password=connection_data.get("password", ""),
                ssl_mode=connection_data.get("ssl_mode", "require"),
                is_active=True
            )
            self.db.add(connection)
            self.db.commit()
            self.db.refresh(connection)
            return True
        except Exception as e:
            print(f"Error saving database connection: {str(e)}")
            return False

    def update_database_connection(self, connection_data: Dict) -> bool:
        """Update an existing database connection"""
        try:
            connection = self.db.query(DatabaseConnection).filter(
                DatabaseConnection.id == connection_data["id"]
            ).first()

            if connection:
                connection.name = connection_data["name"]
                connection.description = connection_data.get("description", "")
                connection.connection_type = connection_data["connection_type"]
                connection.host = connection_data["host"]
                connection.port = connection_data["port"]
                connection.database = connection_data["database"]
                connection.username = connection_data["username"]
                if "password" in connection_data:
                    connection.password = connection_data["password"]
                connection.ssl_mode = connection_data.get("ssl_mode", "require")

                self.db.commit()
                self.db.refresh(connection)
                return True
            return False
        except Exception as e:
            print(f"Error updating database connection: {str(e)}")
            return False

    def test_connection(self, connection_data: Dict) -> bool:
        """Test a database connection"""
        try:
            # If ID is provided, get connection details from database
            if "id" in connection_data:
                connection = self.db.query(DatabaseConnection).filter(
                    DatabaseConnection.id == connection_data["id"]
                ).first()
                if not connection:
                    return False
                connection_data = {
                    "connection_type": connection.connection_type,
                    "host": connection.host,
                    "port": connection.port,
                    "database": connection.database,
                    "username": connection.username,
                    "password": connection.password,
                    "ssl_mode": connection.ssl_mode
                }

            # Create connection string based on database type
            if connection_data["connection_type"] == "postgresql":
                conn_str = (
                    f"postgresql://{connection_data['username']}:{connection_data['password']}"
                    f"@{connection_data['host']}:{connection_data['port']}"
                    f"/{connection_data['database']}"
                )

                # Create test engine
                test_engine = create_engine(
                    conn_str,
                    connect_args={
                        'sslmode': connection_data.get('ssl_mode', 'require'),
                        'connect_timeout': 10
                    }
                )

                # Test connection
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                # Update last_connected_at if this is an existing connection
                if "id" in connection_data:
                    connection.last_connected_at = datetime.utcnow()
                    self.db.commit()

                return True

            return False
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def get_available_tables(self, connection_id: int) -> List[str]:
        """Get available tables for a specific database connection"""
        try:
            # Ensure sample table exists first
            self._ensure_sample_table_exists()

            connection = self.db.query(DatabaseConnection).filter(
                DatabaseConnection.id == connection_id
            ).first()

            if not connection:
                return []

            if connection.connection_type == "postgresql":
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    user=connection.username,
                    password=connection.password,
                    sslmode=connection.ssl_mode
                )
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                return tables

            return []
        except Exception as e:
            print(f"Error getting tables: {str(e)}")
            return []

    def _ensure_sample_table_exists(self):
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sample_table')"
                )).scalar()

                if not result:
                    # Create and populate sample table
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS sample_table (
                            id SERIAL PRIMARY KEY,
                            numeric_value INTEGER,
                            category VARCHAR(50),
                            measurement FLOAT
                        )
                    """))

                    conn.execute(text("""
                        INSERT INTO sample_table (numeric_value, category, measurement)
                        SELECT 
                            floor(random() * 100 + 1)::int,
                            'Category ' || (floor(random() * 5 + 1)::int)::text,
                            random() * 100
                        FROM generate_series(1, 1000)
                    """))
                    conn.commit()
                    print("Sample table created and populated successfully")
        except Exception as e:
            print(f"Error ensuring sample table exists: {str(e)}")

    def get_column_names(self, connection_id: int, table_name: str) -> List[str]:
        """Get column names for a specific table in a database connection"""
        try:
            # First ensure we have a valid connection
            connection = self.db.query(DatabaseConnection).filter(
                DatabaseConnection.id == connection_id
            ).first()

            if not connection:
                print(f"No connection found for id: {connection_id}")
                return []

            if not table_name:
                print("No table name provided")
                return []

            if connection.connection_type == "postgresql":
                # Create connection string
                conn = psycopg2.connect(
                    host=connection.host,
                    port=connection.port,
                    database=connection.database,
                    user=connection.username,
                    password=connection.password,
                    sslmode=connection.ssl_mode
                )

                try:
                    cursor = conn.cursor()

                    # First check if table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT 1 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        );
                    """, (table_name,))

                    table_exists = cursor.fetchone()[0]

                    if not table_exists:
                        print(f"Table {table_name} does not exist")
                        return []

                    # Get column names
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                        ORDER BY ordinal_position;
                    """, (table_name,))

                    columns = [row[0] for row in cursor.fetchall()]
                    print(f"Found columns for {table_name}: {columns}")
                    return columns

                finally:
                    cursor.close()
                    conn.close()

            return []
        except Exception as e:
            print(f"Error getting columns: {str(e)}")
            return []

    def get_rules(self) -> List[Rule]:
        return self.db.query(Rule).all()

    def rule_name_exists(self, name: str) -> bool:
        """Check if a rule with the given name already exists"""
        return self.db.query(Rule).filter(Rule.name == name).first() is not None

    def save_rule(self, rule_data: Dict) -> Rule:
        # Check if rule name already exists
        if self.rule_name_exists(rule_data["name"]):
            raise ValueError(f"A rule with name '{rule_data['name']}' already exists")

        rule = Rule(
            name=rule_data["name"],
            description=rule_data["description"],
            folder=rule_data.get("folder", "/"),
            database=rule_data["database"],
            table=rule_data["table"],
            type=rule_data["type"],
            column=rule_data["column"],
            threshold=rule_data["threshold"],
            parameters=rule_data.get("parameters", {})
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_data: Dict) -> Rule:
        rule = self.db.query(Rule).filter(Rule.id == rule_data["id"]).first()
        if rule:
            rule.name = rule_data["name"]
            rule.description = rule_data["description"]
            rule.folder = rule_data.get("folder", "/")
            rule.database = rule_data["database"]
            rule.table = rule_data["table"]
            rule.type = rule_data["type"]
            rule.column = rule_data["column"]
            rule.threshold = rule_data["threshold"]
            rule.parameters = rule_data.get("parameters", {})
            self.db.commit()
            self.db.refresh(rule)
        return rule

    def get_results(self) -> List[Result]:
        return self.db.query(Result).all()

    def save_result(self, result_data: Dict) -> Result:
        result = Result(
            rule_id=int(result_data["rule_id"]),
            status=str(result_data["status"]),
            score=float(result_data["score"]),
            error=str(result_data["error"]) if result_data.get("error") else None
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_sample_data(self, conn_type: str, query: str, limit: int = 100) -> pd.DataFrame:
        try:
            self._ensure_sample_table_exists()

            with self.engine.connect() as connection:
                if not query or "sample_table" not in query.lower():
                    result = connection.execute(
                        text("SELECT * FROM sample_table LIMIT :limit"),
                        {"limit": limit}
                    )
                else:
                    result = connection.execute(
                        text(f"{query} LIMIT :limit"),
                        {"limit": limit}
                    )

                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df

        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return pd.DataFrame()

    def _ensure_sample_table_exists(self):
        try:
            with self.engine.connect() as conn:
                # Check if table exists
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sample_table')"
                )).scalar()

                if not result:
                    # Create and populate sample table
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS sample_table (
                            id SERIAL PRIMARY KEY,
                            numeric_value INTEGER,
                            category VARCHAR(50),
                            measurement FLOAT
                        )
                    """))

                    conn.execute(text("""
                        INSERT INTO sample_table (numeric_value, category, measurement)
                        SELECT 
                            floor(random() * 100 + 1)::int,
                            'Category ' || (floor(random() * 5 + 1)::int)::text,
                            random() * 100
                        FROM generate_series(1, 1000)
                    """))
                    conn.commit()
                    print("Sample table created and populated successfully")
        except Exception as e:
            print(f"Error ensuring sample table exists: {str(e)}")

    def get_folders(self) -> List[Folder]:
        """Get all folders"""
        return self.db.query(Folder).all()

    def create_folder(self, folder_data: Dict) -> Folder:
        """Create a new folder"""
        try:
            folder = Folder(
                name=folder_data["name"],
                description=folder_data.get("description", ""),
                parent_folder=folder_data.get("parent_folder", "/")
            )
            self.db.add(folder)
            self.db.commit()
            self.db.refresh(folder)
            return folder
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create folder: {str(e)}")

    def folder_exists(self, name: str) -> bool:
        """Check if a folder with the given name exists"""
        return self.db.query(Folder).filter(Folder.name == name).first() is not None

    def get_folder_structure(self) -> Dict[str, List]:
        """Get folder structure with rules"""
        folders = {"/": []}  # Initialize with root folder

        # Add all folders from database
        db_folders = self.get_folders()
        for folder in db_folders:
            folders[folder.name] = []

        # Add rules to their respective folders
        rules = self.get_rules()
        for rule in rules:
            folder = rule.folder if rule.folder in folders else "/"
            folders[folder].append(rule)

        return folders