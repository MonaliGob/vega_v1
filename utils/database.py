import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from .models import get_db, Rule, Result, engine
import os
import psycopg2
from psycopg2 import sql

class DatabaseConnector:
    def __init__(self):
        self.db = next(get_db())
        # Use the same engine from models.py
        self.engine = engine

        # Connection settings for direct psycopg2 connections
        self.connections = {
            "postgres": {
                "host": os.getenv('PGHOST'),
                "port": os.getenv('PGPORT'),
                "user": os.getenv('PGUSER'),
                "password": os.getenv('PGPASSWORD'),
                "database": os.getenv('PGDATABASE'),
                "sslmode": "require",
                "connect_timeout": 30,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        }

    def get_available_connections(self) -> List[str]:
        return list(self.connections.keys())

    def get_available_tables(self, conn_type: str) -> List[str]:
        if conn_type == "postgres":
            try:
                conn = psycopg2.connect(**self.connections[conn_type])
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    AND table_name != 'rules'
                    AND table_name != 'results'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                return tables
            except Exception as e:
                print(f"Error getting tables: {str(e)}")
                return []
        return []

    def get_column_names(self, conn_type: str, table_name: str) -> List[str]:
        if not table_name:
            return []

        if conn_type == "postgres":
            try:
                conn = psycopg2.connect(**self.connections[conn_type])
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                columns = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                return columns
            except Exception as e:
                print(f"Error getting columns for {table_name}: {str(e)}")
                return []
        return []

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

    def save_rule(self, rule_data: Dict) -> Rule:
        rule = Rule(
            name=rule_data["name"],
            description=rule_data["description"],
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
            rule.database = rule_data["database"]
            rule.table = rule_data["table"]
            rule.type = rule_data["type"]
            rule.column = rule_data["column"]
            rule.threshold = rule_data["threshold"]
            rule.parameters = rule_data.get("parameters", {})
            self.db.commit()
            self.db.refresh(rule)
        return rule

    def get_rules(self) -> List[Rule]:
        return self.db.query(Rule).all()

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

    def get_results(self) -> List[Result]:
        return self.db.query(Result).all()