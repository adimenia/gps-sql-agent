# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sports analytics platform that ingests GPS performance data from Catapult Sports API, stores it in PostgreSQL, and provides both dashboard analytics and conversational data exploration through a natural language SQL agent.

## Current Implementation Status

The project has completed Phase 1 development with a fully implemented modular ETL system, database schema, FastAPI backend foundation, and comprehensive testing infrastructure. The original monolithic ETL script has been successfully refactored into a production-ready modular architecture. The SQL agent and React frontend are the next components to be implemented.

## Development Commands

### ETL Pipeline
```bash
# Run the complete ETL pipeline
cd backend && python3 app/etl/cli.py run

# Test API connection
python3 app/etl/cli.py test

# Run dry-run (extract and transform only)
python3 app/etl/cli.py dry-run

# Set required environment variables
export CATAPULT_API_TOKEN=your_catapult_api_token_here
```

### Database Management
```bash
# Check database connection
cd backend && python3 manage.py check

# Create initial migration
python3 manage.py init

# Run migrations
python3 manage.py upgrade
```

### Testing
```bash
# Run all tests
cd backend && python3 run_tests.py

# Run specific test categories
python3 run_tests.py --unit
python3 run_tests.py --integration
python3 run_tests.py --etl
```

### Database Connection
- **Host**: localhost
- **Database**: sports_data
- **User**: postgres  
- **Password**: P@ssw0rd
- **Port**: 5432 (default)

## Architecture Overview

### Planned System Flow
```
Catapult API → ETL Service → PostgreSQL → FastAPI Backend → React Frontend
                                    ↓
                              SQL Agent (LLM) ← Chat Interface
```

### Current Implementation
- **ETL Service**: Production-ready modular system (`backend/app/etl/`)
- **Database**: PostgreSQL with SQLAlchemy models and Alembic migrations
- **API Backend**: FastAPI foundation with health endpoints
- **Testing**: Comprehensive test suite with 32+ passing tests
- **Architecture**: Clean modular design with separation of concerns

## Database Schema

The ETL script creates and populates these key tables:
- `activities` - Training sessions and games
- `athletes` - Player information and physical attributes  
- `events` - Performance events (acceleration, jumps, movement analysis)
- `efforts` - Velocity and acceleration efforts by band/intensity
- `periods` - Time segments within activities
- `positions` - Player positions and roles
- `parameters` - Available performance metrics
- `owners` - Team/organization information

## File Organization Guidelines

- Keep files under 500 lines (refactor when approaching limit)  
- Follow modular architecture as described in `PLANNING.md`
- Reference `TASK.md` for implementation priorities
- Use proper logging throughout (already configured in main script)

## Key Implementation Notes

### ETL Process
- Uses batch processing with conflict resolution (`ON CONFLICT DO NOTHING`)
- Implements proper error handling and logging with rotation
- Fetches data incrementally by activity and athlete
- Transforms Unix timestamps to ISO format for database storage

### Data Relationships
- Activities contain multiple periods and athletes
- Athletes participate in multiple activities
- Events and efforts are linked to specific activity-athlete combinations
- Positions and parameters are reference data

### API Integration
- Uses Catapult Sports EU API (connect-eu.catapultsports.com)
- Requires Bearer token authentication
- Implements rate limiting and error handling
- Supports multiple event types: ima_acceleration, ima_jump, football_movement_analysis

## Next Development Steps

Based on `TASK.md`, the next priorities are:
1. **Refactor existing ETL script** into modular components following planned architecture
2. Backend Infrastructure (FastAPI setup, Docker configuration)
3. Database schema migrations (Alembic) - formalize the current ad-hoc schema
4. API endpoints for dashboard and SQL agent
5. Frontend React application
6. Natural language to SQL conversion service

## Refactoring Considerations

The current `catapult_sports_data_ingestion.py` script needs refactoring to:
- Break the 768-line monolithic class into separate extractor, transformer, and loader modules
- Implement proper async/await patterns for API calls
- Add proper configuration management (environment variables, config files)
- Separate database models from ETL logic
- Implement proper error handling and retry mechanisms
- Add unit tests for individual components
- Follow the planned directory structure from `PLANNING.md`

## Performance Considerations

- Database queries should use proper indexing on timestamp and ID fields
- ETL process logs to rotating files (5MB max, 3 backups)
- Batch inserts used for efficiency
- Connection pooling recommended for production API