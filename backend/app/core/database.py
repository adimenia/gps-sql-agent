from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """FastAPI dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database."""
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)

def check_database_connection():
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False