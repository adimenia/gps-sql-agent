#!/usr/bin/env python3
"""Management script for database operations."""

import os
import sys
import argparse
from alembic.config import Config
from alembic import command

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import check_database_connection, create_tables
from app.models import Base


def init_alembic():
    """Initialize Alembic repository."""
    alembic_cfg = Config("alembic.ini")
    command.init(alembic_cfg, "alembic")
    print("Alembic initialized!")


def create_migration(message):
    """Create a new migration."""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    print(f"Migration created: {message}")


def run_migrations():
    """Run all pending migrations."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed!")


def rollback_migration(revision="base"):
    """Rollback to a specific revision."""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    print(f"Rolled back to: {revision}")


def check_db():
    """Check database connection."""
    if check_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        sys.exit(1)


def create_initial_migration():
    """Create initial migration from existing models."""
    alembic_cfg = Config("alembic.ini")
    command.revision(
        alembic_cfg, 
        message="Initial migration with all sports tables", 
        autogenerate=True
    )
    print("Initial migration created!")


def main():
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check database connection
    subparsers.add_parser("check", help="Check database connection")

    # Create migration
    migrate_parser = subparsers.add_parser("migrate", help="Create a new migration")
    migrate_parser.add_argument("message", help="Migration message")

    # Run migrations
    subparsers.add_parser("upgrade", help="Run all pending migrations")

    # Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument("--revision", default="base", help="Revision to rollback to")

    # Initial migration
    subparsers.add_parser("init", help="Create initial migration")

    args = parser.parse_args()

    if args.command == "check":
        check_db()
    elif args.command == "migrate":
        create_migration(args.message)
    elif args.command == "upgrade":
        run_migrations()
    elif args.command == "rollback":
        rollback_migration(args.revision)
    elif args.command == "init":
        create_initial_migration()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()