from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

# Update engine configuration with proper SSL settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    connect_args={
        'sslmode': 'require',
        'connect_timeout': 30,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    connection_type = Column(String)  # postgresql, mysql, etc.
    host = Column(String)
    port = Column(Integer)
    database = Column(String)
    username = Column(String)
    password = Column(String)
    ssl_mode = Column(String, default='require')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_connected_at = Column(DateTime, nullable=True)

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    folder = Column(String, default="/")  # Root folder by default
    database = Column(String)
    table = Column(String)
    type = Column(String)
    column = Column(String)
    threshold = Column(Float)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, index=True)
    status = Column(String)
    score = Column(Float)
    error = Column(String, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def init_db():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # Create and populate sample table if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text("""
                DROP TABLE IF EXISTS sample_table;
                CREATE TABLE sample_table (
                    id SERIAL PRIMARY KEY,
                    numeric_value INTEGER,
                    category VARCHAR(50),
                    measurement FLOAT
                );
            """))

            # Populate with sample data
            conn.execute(text("""
                INSERT INTO sample_table (numeric_value, category, measurement)
                SELECT 
                    floor(random() * 100 + 1)::int,
                    'Category ' || (floor(random() * 5 + 1)::int)::text,
                    random() * 100
                FROM generate_series(1, 1000);
            """))
            conn.commit()
            print("Sample table created and populated successfully")

            # Create a default database connection if none exists
            result = conn.execute(text("SELECT COUNT(*) FROM database_connections")).scalar()
            if result == 0:
                conn.execute(text("""
                    INSERT INTO database_connections (
                        name, description, connection_type, host, port, 
                        database, username, password, ssl_mode, is_active
                    ) VALUES (
                        'Default PostgreSQL', 'Default local connection', 'postgresql',
                        :host, :port, :database, :username, :password, 'require', true
                    )
                """), {
                    'host': os.getenv('PGHOST'),
                    'port': int(os.getenv('PGPORT')),
                    'database': os.getenv('PGDATABASE'),
                    'username': os.getenv('PGUSER'),
                    'password': os.getenv('PGPASSWORD')
                })
                conn.commit()
                print("Default database connection created")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()