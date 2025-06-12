#!/usr/bin/env python3
"""Create database tables directly."""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from app.models.base import Base

def create_tables():
    """Create all database tables."""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)