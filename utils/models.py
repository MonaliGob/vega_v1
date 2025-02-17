from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
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
    connection_id = Column(Integer)  # Reference to DatabaseConnection
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
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()