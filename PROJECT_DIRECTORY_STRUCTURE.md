# 📁 Sports Analytics Platform - Directory Structure

```
sports-analytics-platform/
├── README.md                           # Project overview and setup guide
├── PLANNING.md                         # Architecture and design decisions
├── TASK.md                            # Implementation task breakdown
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore patterns
├── docker-compose.yml                 # Local development environment
├── docker-compose.prod.yml            # Production deployment
├── LICENSE                            # Project license
│
├── backend/                           # Python FastAPI backend
│   ├── Dockerfile                     # Backend container definition
│   ├── requirements.txt               # Python dependencies
│   ├── requirements-dev.txt           # Development dependencies
│   ├── pyproject.toml                 # Python project configuration
│   ├── alembic.ini                    # Database migration configuration
│   │
│   ├── app/                           # Main application package
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   │
│   │   ├── core/                      # Core configuration and utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Application configuration
│   │   │   ├── database.py            # Database connection and session
│   │   │   ├── logging.py             # Logging configuration
│   │   │   ├── cache.py               # Caching utilities
│   │   │   └── security.py            # Security utilities
│   │   │
│   │   ├── models/                    # Database models and schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model classes
│   │   │   ├── athlete.py             # Athlete model
│   │   │   ├── period.py              # Period model
│   │   │   ├── event.py               # Event model
│   │   │   ├── effort.py              # Effort model
│   │   │   └── parameter.py           # Parameter model
│   │   │
│   │   ├── schemas/                   # Pydantic schemas for API
│   │   │   ├── __init__.py
│   │   │   ├── athlete.py             # Athlete request/response schemas
│   │   │   ├── period.py              # Period request/response schemas
│   │   │   ├── event.py               # Event request/response schemas
│   │   │   ├── chat.py                # Chat request/response schemas
│   │   │   └── dashboard.py           # Dashboard request/response schemas
│   │   │
│   │   ├── api/                       # FastAPI route definitions
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # API dependencies
│   │   │   ├── health.py              # Health check endpoints
│   │   │   ├── periods.py             # Period CRUD endpoints
│   │   │   ├── athletes.py            # Athlete CRUD endpoints
│   │   │   ├── events.py              # Event data endpoints
│   │   │   ├── efforts.py             # Effort data endpoints
│   │   │   ├── dashboard.py           # Dashboard metrics endpoints
│   │   │   ├── chat.py                # Chat/Agent endpoints
│   │   │   └── etl.py                 # ETL trigger endpoints
│   │   │
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── athlete_service.py     # Athlete business logic
│   │   │   ├── period_service.py      # Period business logic
│   │   │   ├── analytics_service.py   # Analytics calculations
│   │   │   └── dashboard_service.py   # Dashboard data aggregation
│   │   │
│   │   ├── etl/                       # Extract, Transform, Load services
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py        # ETL workflow coordinator
│   │   │   ├── scheduler.py           # ETL scheduling service
│   │   │   ├── catapult_client.py     # Catapult API client
│   │   │   │
│   │   │   ├── extractors/            # Data extraction modules
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py            # Base extractor class
│   │   │   │   ├── periods.py         # Periods data extractor
│   │   │   │   ├── athletes.py        # Athletes data extractor
│   │   │   │   ├── events.py          # Events data extractor
│   │   │   │   └── efforts.py         # Efforts data extractor
│   │   │   │
│   │   │   ├── transformers/          # Data transformation modules
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py            # Base transformer class
│   │   │   │   ├── periods.py         # Periods data transformer
│   │   │   │   ├── athletes.py        # Athletes data transformer
│   │   │   │   ├── events.py          # Events data transformer
│   │   │   │   └── efforts.py         # Efforts data transformer
│   │   │   │
│   │   │   └── loaders/               # Data loading modules
│   │   │       ├── __init__.py
│   │   │       ├── base.py            # Base loader class
│   │   │       ├── periods.py         # Periods data loader
│   │   │       ├── athletes.py        # Athletes data loader
│   │   │       ├── events.py          # Events data loader
│   │   │       └── efforts.py         # Efforts data loader
│   │   │
│   │   └── agent/                     # SQL Agent and NLP processing
│   │       ├── __init__.py
│   │       ├── orchestrator.py        # Agent workflow coordinator
│   │       ├── llm_client.py          # LLM API client (OpenAI/Anthropic)
│   │       ├── nl_to_sql.py           # Natural language to SQL conversion
│   │       ├── sql_executor.py        # Safe SQL execution
│   │       ├── explainer.py           # Result explanation generator
│   │       ├── security.py            # SQL injection prevention
│   │       └── prompts/               # LLM prompt templates
│   │           ├── __init__.py
│   │           ├── sql_generation.py  # SQL generation prompts
│   │           └── explanation.py     # Explanation prompts
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── versions/                  # Migration files
│   │   ├── env.py                     # Alembic environment
│   │   └── script.py.mako             # Migration template
│   │
│   └── tests/                         # Backend test suite
│       ├── __init__.py
│       ├── conftest.py                # Pytest configuration and fixtures
│       ├── test_database.py           # Database test fixtures
│       │
│       ├── api/                       # API endpoint tests
│       │   ├── __init__.py
│       │   ├── test_health.py         # Health endpoint tests
│       │   ├── test_periods.py        # Periods API tests
│       │   ├── test_athletes.py       # Athletes API tests
│       │   ├── test_dashboard.py      # Dashboard API tests
│       │   └── test_chat.py           # Chat API tests
│       │
│       ├── services/                  # Service layer tests
│       │   ├── __init__.py
│       │   ├── test_athlete_service.py
│       │   ├── test_period_service.py
│       │   └── test_analytics_service.py
│       │
│       ├── etl/                       # ETL process tests
│       │   ├── __init__.py
│       │   ├── test_orchestrator.py   # ETL workflow tests
│       │   ├── test_extractors.py     # Data extraction tests
│       │   ├── test_transformers.py   # Data transformation tests
│       │   └── test_loaders.py        # Data loading tests
│       │
│       ├── agent/                     # SQL Agent tests
│       │   ├── __init__.py
│       │   ├── test_nl_to_sql.py      # NL to SQL conversion tests
│       │   ├── test_sql_executor.py   # SQL execution tests
│       │   ├── test_explainer.py      # Explanation generation tests
│       │   └── test_security.py       # Security validation tests
│       │
│       └── integration/               # Integration tests
│           ├── __init__.py
│           ├── test_etl_pipeline.py   # End-to-end ETL tests
│           ├── test_agent_workflow.py # End-to-end agent tests
│           └── test_api_integration.py # Full API integration tests
│
├── frontend/                          # React TypeScript frontend
│   ├── Dockerfile                     # Frontend container definition
│   ├── package.json                   # Node.js dependencies
│   ├── package-lock.json              # Dependency lock file
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── vite.config.ts                 # Vite build configuration
│   ├── index.html                     # Main HTML template
│   ├── .eslintrc.js                   # ESLint configuration
│   ├── .prettierrc                    # Prettier configuration
│   │
│   ├── public/                        # Static assets
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── robots.txt
│   │
│   ├── src/                           # Source code
│   │   ├── main.tsx                   # Application entry point
│   │   ├── App.tsx                    # Main App component
│   │   ├── vite-env.d.ts              # Vite type definitions
│   │   │
│   │   ├── components/                # Reusable UI components
│   │   │   ├── Layout/                # Layout components
│   │   │   │   ├── Header.tsx         # App header
│   │   │   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   │   │   ├── Footer.tsx         # App footer
│   │   │   │   └── MainLayout.tsx     # Main layout wrapper
│   │   │   │
│   │   │   ├── Charts/                # Data visualization components
│   │   │   │   ├── LineChart.tsx      # Line chart component
│   │   │   │   ├── BarChart.tsx       # Bar chart component
│   │   │   │   ├── ScatterPlot.tsx    # Scatter plot component
│   │   │   │   └── ChartContainer.tsx # Chart wrapper with loading
│   │   │   │
│   │   │   ├── Chat/                  # Chat interface components
│   │   │   │   ├── ChatInterface.tsx  # Main chat component
│   │   │   │   ├── MessageList.tsx    # Message history display
│   │   │   │   ├── MessageInput.tsx   # Chat input component
│   │   │   │   ├── Message.tsx        # Individual message component
│   │   │   │   └── TypingIndicator.tsx # Typing indicator
│   │   │   │
│   │   │   ├── Filters/               # Data filtering components
│   │   │   │   ├── DateRangePicker.tsx # Date range selection
│   │   │   │   ├── AthleteFilter.tsx  # Athlete selection filter
│   │   │   │   ├── PositionFilter.tsx # Position filter
│   │   │   │   └── FilterPanel.tsx    # Combined filter panel
│   │   │   │
│   │   │   ├── Dashboard/             # Dashboard-specific components
│   │   │   │   ├── MetricCard.tsx     # KPI display card
│   │   │   │   ├── MetricGrid.tsx     # Grid of metric cards
│   │   │   │   ├── TrendChart.tsx     # Performance trend visualization
│   │   │   │   └── SummaryStats.tsx   # Summary statistics display
│   │   │   │
│   │   │   └── Common/                # Common UI components
│   │   │       ├── LoadingSpinner.tsx # Loading indicator
│   │   │       ├── ErrorBoundary.tsx  # Error handling component
│   │   │       ├── NotFound.tsx       # 404 component
│   │   │       └── ConfirmDialog.tsx  # Confirmation dialog
│   │   │
│   │   ├── pages/                     # Page-level components
│   │   │   ├── Dashboard.tsx          # Main dashboard page
│   │   │   ├── Athletes.tsx           # Athletes overview page
│   │   │   ├── Periods.tsx            # Periods overview page
│   │   │   ├── Analytics.tsx          # Advanced analytics page
│   │   │   └── Settings.tsx           # Application settings page
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useApi.ts              # API communication hook
│   │   │   ├── useAuth.ts             # Authentication hook (future)
│   │   │   ├── useWebSocket.ts        # WebSocket connection hook
│   │   │   ├── useFilters.ts          # Filter state management hook
│   │   │   ├── useLocalStorage.ts     # Local storage hook
│   │   │   └── useDebounce.ts         # Debounce utility hook
│   │   │
│   │   ├── services/                  # API and external services
│   │   │   ├── api.ts                 # Main API client
│   │   │   ├── websocket.ts           # WebSocket service
│   │   │   ├── athleteService.ts      # Athlete API calls
│   │   │   ├── periodService.ts       # Period API calls
│   │   │   ├── dashboardService.ts    # Dashboard API calls
│   │   │   └── chatService.ts         # Chat API calls
│   │   │
│   │   ├── types/                     # TypeScript type definitions
│   │   │   ├── api.ts                 # API response types
│   │   │   ├── athlete.ts             # Athlete data types
│   │   │   ├── period.ts              # Period data types
│   │   │   ├── event.ts               # Event data types
│   │   │   ├── chat.ts                # Chat message types
│   │   │   └── dashboard.ts           # Dashboard data types
│   │   │
│   │   ├── utils/                     # Utility functions
│   │   │   ├── formatters.ts          # Data formatting utilities
│   │   │   ├── validators.ts          # Input validation functions
│   │   │   ├── dateUtils.ts           # Date manipulation utilities
│   │   │   ├── chartUtils.ts          # Chart configuration utilities
│   │   │   └── constants.ts           # Application constants
│   │   │
│   │   ├── styles/                    # Styling and themes
│   │   │   ├── theme.ts               # Material-UI/Chakra theme
│   │   │   ├── globals.css            # Global CSS styles
│   │   │   └── variables.css          # CSS custom properties
│   │   │
│   │   └── context/                   # React context providers
│   │       ├── AppContext.tsx         # Global app state context
│   │       ├── FilterContext.tsx      # Filter state context
│   │       └── ThemeContext.tsx       # Theme context
│   │
│   └── tests/                         # Frontend test suite
│       ├── setup.ts                   # Test setup configuration
│       ├── __mocks__/                 # Mock implementations
│       │   ├── api.ts                 # API mock
│       │   └── websocket.ts           # WebSocket mock
│       │
│       ├── components/                # Component tests
│       │   ├── Dashboard.test.tsx     # Dashboard component tests
│       │   ├── Chat.test.tsx          # Chat component tests
│       │   ├── Charts.test.tsx        # Chart component tests
│       │   └── Filters.test.tsx       # Filter component tests
│       │
│       ├── hooks/                     # Hook tests
│       │   ├── useApi.test.ts         # API hook tests
│       │   ├── useWebSocket.test.ts   # WebSocket hook tests
│       │   └── useFilters.test.ts     # Filter hook tests
│       │
│       ├── services/                  # Service tests
│       │   ├── api.test.ts            # API service tests
│       │   └── websocket.test.ts      # WebSocket service tests
│       │
│       └── integration/               # Integration tests
│           ├── dashboard.test.tsx     # Dashboard integration tests
│           ├── chat.test.tsx          # Chat integration tests
│           └── filters.test.tsx       # Filter integration tests
│
├── docs/                              # Additional documentation
│   ├── api/                           # API documentation
│   │   ├── endpoints.md               # API endpoint documentation
│   │   ├── schemas.md                 # Data schema documentation
│   │   └── examples.md                # API usage examples
│   │
│   ├── deployment/                    # Deployment guides
│   │   ├── local.md                   # Local development setup
│   │   ├── production.md              # Production deployment guide
│   │   └── troubleshooting.md         # Common issues and solutions
│   │
│   ├── architecture/                  # Architecture documentation
│   │   ├── overview.md                # System architecture overview
│   │   ├── database.md                # Database design documentation
│   │   ├── etl.md                     # ETL process documentation
│   │   └── agent.md                   # SQL Agent design documentation
│   │
│   └── images/                        # Documentation images
│       ├── architecture-diagram.png   # System architecture diagram
│       ├── database-schema.png        # Database schema diagram
│       └── user-flow.png              # User interaction flow
│
└── scripts/                           # Utility scripts
    ├── setup.sh                       # Initial project setup script
    ├── test.sh                        # Run all tests script
    ├── deploy.sh                      # Deployment script
    ├── db-reset.sh                    # Database reset script (dev only)
    ├── generate-docs.sh               # API documentation generation
    └── backup.sh                      # Database backup script
```

## 📋 Key Design Principles

### File Organization
- **Modular Structure**: Each component has a clear responsibility and stays under 500 lines
- **Separation of Concerns**: Business logic, API routes, and data models are separated
- **Consistent Naming**: Use clear, descriptive names for files and directories
- **Scalable Architecture**: Easy to add new features without major restructuring

### Backend Structure
- **Core**: Application configuration, database setup, utilities
- **Models**: Database entities and relationships
- **Schemas**: API request/response validation
- **Services**: Business logic separated from API routes
- **ETL**: Modular extract, transform, load pipeline
- **Agent**: Natural language processing and SQL generation
- **API**: Clean REST endpoints with proper HTTP methods
- **Tests**: Comprehensive testing strategy with proper mocking

### Frontend Structure
- **Components**: Reusable UI components organized by feature
- **Pages**: Top-level route components
- **Hooks**: Custom React hooks for shared logic
- **Services**: API communication and external service integration
- **Types**: Centralized TypeScript type definitions
- **Utils**: Pure utility functions and constants

### Testing Strategy
- **Unit Tests**: Individual function and component testing
- **Integration Tests**: Feature-level testing with real dependencies
- **E2E Tests**: Complete user workflow testing
- **Mocking**: Proper isolation of external dependencies

This structure follows the AI Coding Assistant Workflow principles of modularity, testability, and maintainability while keeping files under the 500-line limit.