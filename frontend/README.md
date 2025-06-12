# Sports Analytics Platform - Frontend

A React TypeScript frontend for the Sports Analytics Platform with SQL Agent.

## Features

- 🤖 **Chat Interface** - Natural language interaction with AI SQL Agent
- 📊 **Dashboard** - Overview of sports analytics data
- 🔄 **Real-time Data** - Live communication with backend APIs
- 📱 **Responsive Design** - Works on desktop and mobile
- ⚡ **Fast Development** - Vite for lightning-fast builds

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **React Router** for navigation
- **Axios** for API communication
- **CSS3** for styling (no external UI library yet)

## Getting Started

### Prerequisites

- Node.js 18+ 
- Backend server running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Check TypeScript types
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.tsx      # Main layout with navigation
├── pages/              # Page components
│   ├── Dashboard.tsx   # Dashboard overview
│   └── Chat.tsx        # AI chat interface
├── services/           # API communication
│   └── api.ts          # Backend API service
├── hooks/              # Custom React hooks
│   └── useApi.ts       # API and async operation hooks
├── types/              # TypeScript type definitions
│   └── index.ts        # Common types
├── App.tsx             # Main app component
├── main.tsx            # React entry point
└── index.css           # Global styles
```

## API Integration

The frontend connects to the backend API at `/api/v1/*` with automatic proxy configuration.

### Key API Endpoints Used

- `GET /api/v1/dashboard/metrics/overview` - Dashboard stats
- `POST /api/v1/chat/ask` - Send questions to AI agent
- `GET /api/v1/health/` - System health check

## Development Notes

### Current State: Basic Functional UI

This is a minimal, functional frontend focused on core features:

- ✅ Basic dashboard with key metrics
- ✅ Chat interface for SQL Agent interaction  
- ✅ Clean navigation and routing
- ✅ API integration with error handling
- ✅ TypeScript for type safety

### Next Phase: UI Enhancement

Future improvements planned:
- UI component library (Material-UI/Chakra UI)
- Advanced charts and visualizations
- Enhanced chat interface with syntax highlighting
- Responsive design improvements
- Loading states and animations

## Environment Variables

Create `.env.local` if needed:

```env
VITE_API_URL=http://localhost:8000
```

## Chat Interface

The chat interface allows natural language questions like:

- "How many athletes are in the database?"
- "Who are the top 5 fastest athletes?"
- "Show me recent training activities"
- "What's the average velocity for defenders?"

Results include:
- Direct answers from the SQL Agent
- Raw data when applicable
- Performance insights and context
- Sports-specific explanations

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Keep components under 200 lines
4. Add proper error handling
5. Test chat functionality with backend

## Troubleshooting

### Common Issues

**Frontend won't start:**
- Ensure Node.js 18+ is installed
- Run `npm install` to install dependencies
- Check port 3000 is available

**API calls failing:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify proxy configuration in vite.config.ts

**Chat not working:**
- Test backend SQL Agent with `curl -X POST http://localhost:8000/api/v1/chat/test`
- Check browser network tab for failed requests
- Verify LLM API keys are configured in backend

---

**Ready to chat with your sports data! 🏃‍♂️💬**