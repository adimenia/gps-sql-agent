# 🏃‍♂️ Sports Analytics Platform

An intelligent sports analytics platform that automatically ingests performance data from Catapult Sports API, stores it in PostgreSQL, and provides both dashboard analytics and conversational data exploration through a natural language SQL agent.

## 🎯 Overview

This platform combines automated data pipelines with intelligent querying capabilities, allowing sports analysts and coaches to explore performance data through both traditional dashboards and natural language conversations.

### Key Features

- **📊 Automated Data Pipeline**: Scheduled extraction and storage of Catapult Sports API data
- **🤖 Intelligent SQL Agent**: Ask questions about your data in plain English
- **📈 Interactive Dashboard**: Real-time metrics with dynamic filtering
- **💬 Chat Interface**: Conversational data exploration with detailed explanations
- **🔍 Advanced Analytics**: Performance trends, athlete comparisons, and insights

## 🏗️ Architecture Overview

### System Flow
```
Catapult API → ETL Service → PostgreSQL → FastAPI Backend → React Frontend
                                    ↓
                              SQL Agent (LLM) ← Chat Interface
```

### Backend Components
- **ETL Service**: Handles scheduled data extraction, transformation, and loading
- **FastAPI Backend**: REST API with WebSocket support for real-time chat
- **SQL Agent**: Natural language to SQL conversion with intelligent explanations
- **PostgreSQL**: Optimized database schema for sports performance data

### Frontend Components
- **Dashboard**: Interactive charts and metrics with filtering capabilities
- **Chat Interface**: Conversational SQL agent for data exploration
- **Real-time Updates**: Live data synchronization and notifications

## 🛠️ Technologies Used

### Backend
- **Python 3.11+** - Core backend language
- **FastAPI** - Async web framework with auto-documentation
- **PostgreSQL** - Primary database with time-series optimization
- **SQLAlchemy/SQLModel** - ORM with type safety
- **Pydantic** - Data validation and serialization
- **OpenAI/Anthropic** - LLM integration for natural language processing

### Frontend
- **React 18** with TypeScript for type safety
- **React Query** - Server state management and caching
- **Material-UI/Chakra UI** - Component library for rapid development
- **Recharts** - Data visualization and charting
- **WebSocket** - Real-time communication for chat interface

### Infrastructure
- **Docker & Docker Compose** - Containerization and local development
- **PostgreSQL** - Primary database with performance optimizations
- **Redis** (optional) - Caching layer for improved performance

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- (Optional) Node.js 18+ and Python 3.11+ for local development

### 1. Clone and Setup
```bash
git clone <repository-url>
cd sports-analytics-platform
cp .env.example .env
# Edit .env with your Catapult API credentials and other configurations
```

### 2. Environment Configuration
Create a `.env` file with the following variables:
```env
# Catapult API Configuration
CATAPULT_API_URL=https://connect-eu.catapultsports.com/api/v6
CATAPULT_API_TOKEN=your_api_token_here

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sports_analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
ETL_SCHEDULE_HOURS=6  # Run ETL every 6 hours
```

### 3. Run with Docker Compose
```bash
# Start all services (database, backend, frontend)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access the Application
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (use your preferred PostgreSQL client)

### 5. Initial Data Setup
```bash
# Run initial ETL to populate the database
docker-compose exec backend python -m app.etl.run_initial_sync

# Or trigger via API
curl -X POST http://localhost:8000/api/v1/etl/trigger
```

## 🧪 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Database Management
```bash
# Apply migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Reset database (development only)
docker-compose down -v
docker-compose up -d database
```

## 📊 Usage Examples

### Dashboard Analytics
- View key performance metrics across all athletes and time periods
- Filter data by date ranges, athlete positions, or specific activities
- Compare performance trends between athletes or time periods
- Export charts and data for reporting

### SQL Agent Chat Examples
```
User: "What was the average velocity for all defenders last week?"
Agent: Based on the data, defenders averaged 4.2 m/s velocity last week...

User: "Show me the top 3 performers in acceleration during Period 1"
Agent: Here are the top acceleration performers in Period 1: [detailed analysis]

User: "Compare John's performance this month vs last month"
Agent: John's performance comparison shows improvements in... [detailed breakdown]
```

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
docker-compose exec backend pytest tests/ -v --cov=app

# Frontend tests
docker-compose exec frontend npm test

# Integration tests
docker-compose exec backend pytest tests/integration/ -v
```

### Test Categories
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Database operations and API endpoints
- **E2E Tests**: Complete user workflows
- **Performance Tests**: Database query optimization and load testing

## 📁 Project Structure

```
sports-analytics-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes and endpoints
│   │   ├── agent/        # SQL Agent and NLP processing
│   │   ├── etl/          # Data extraction, transformation, loading
│   │   ├── models/       # Database models and schemas
│   │   ├── services/     # Business logic services
│   │   └── core/         # Configuration and utilities
│   ├── tests/            # Backend test suite
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page-level components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API communication
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── package.json
├── docker-compose.yml    # Local development environment
├── docker-compose.prod.yml  # Production deployment
├── PLANNING.md          # Detailed architecture and planning
├── TASK.md             # Implementation task breakdown
└── README.md           # This file
```

## 🤝 Contributing

### Development Workflow
1. Read `PLANNING.md` for architecture understanding
2. Check `TASK.md` for available tasks
3. Create feature branch from `main`
4. Follow code style guidelines (Black for Python, Prettier for TypeScript)
5. Write tests for new features
6. Update documentation as needed
7. Submit pull request with clear description

### Code Style
- **Python**: Follow PEP8, use Black formatter, include type hints
- **TypeScript**: Use Prettier, prefer functional components with hooks
- **Documentation**: Update README.md and inline comments for complex logic
- **Testing**: Aim for 90%+ coverage on new code

### File Organization
- Keep files under 500 lines (refactor into modules when needed)
- Use clear, descriptive naming conventions
- Group related functionality into modules
- Include docstrings for all public functions

## 📈 Performance & Monitoring

### Key Metrics
- **ETL Performance**: Data sync duration and success rates
- **Query Performance**: Dashboard load times and SQL Agent response times
- **User Experience**: Frontend responsiveness and error rates
- **Data Quality**: Validation success rates and data freshness

### Monitoring Endpoints
- **Health Check**: `GET /health`
- **Database Status**: `GET /health/database`
- **ETL Status**: `GET /health/etl`
- **API Metrics**: Available at `/metrics` (Prometheus format)

## 🆘 Troubleshooting

### Common Issues

**ETL Job Failures**
```bash
# Check ETL logs
docker-compose logs etl

# Manually trigger ETL
curl -X POST http://localhost:8000/api/v1/etl/trigger

# Check database connectivity
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

**Database Connection Issues**
```bash
# Restart database
docker-compose restart database

# Check PostgreSQL logs
docker-compose logs database

# Verify connection parameters in .env
```

**Frontend Build Issues**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions, issues, or contributions:
- Create an issue in this repository
- Check existing documentation in `/docs`
- Review `PLANNING.md` for architectural decisions
- Contact the development team

---

**Happy Analyzing! 🏃‍♂️📊**