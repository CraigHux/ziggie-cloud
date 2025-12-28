# Ziggie Control Center - Frontend

**Version:** 1.0.0
**Architecture:** React with Vite and Material-UI
**Purpose:** Web-based dashboard for Ziggie Control Center workspace management
**Port:** 3001

---

## Overview

The Ziggie Control Center Frontend is a modern React application providing a beautiful, responsive dashboard for managing multiple workspaces, services, AI agents, and the knowledge base. Built with Vite for fast development and Material-UI for professional styling.

## Features

- **Dashboard:** Real-time system stats, service status, and quick actions
- **Services Management:** Start, stop, restart services with live logs
- **System Monitor:** Process list, port scanner, and system information
- **Real-time Updates:** WebSocket connection for live data via `/api/system/ws`
- **Beautiful UI:** Material-UI with dark/light mode support
- **Responsive Design:** Works on desktop and mobile
- **Agent Management:** Monitor and interact with 584 AI agents
- **Knowledge Base Browser:** Search and view knowledge files
- **Workspace Integration:** Support for Meow Ping RTS, ComfyUI, and more

## Tech Stack

- **React 18:** Modern React with hooks
- **Vite:** Fast build tool and dev server
- **Material-UI:** Beautiful component library
- **TypeScript:** Type-safe JavaScript
- **React Router:** Client-side routing
- **Recharts:** Data visualization
- **Axios:** HTTP client
- **WebSocket:** Real-time communication
- **TailwindCSS:** Utility-first CSS

## Installation & Setup

### Docker Setup (Recommended)

```bash
# From project root
docker-compose up -d

# Frontend will be available at http://localhost:3001
```

### Local Development Setup

**Prerequisites:**
- Node.js 18+ and npm
- Backend API running on `http://localhost:54112`

**Installation:**
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will open at `http://localhost:3001`

### Environment Configuration

Create `.env` file in `frontend/` directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:54112
REACT_APP_API_TIMEOUT=10000

# WebSocket Configuration
REACT_APP_WS_URL=ws://localhost:54112
REACT_APP_WS_UPDATE_INTERVAL=2000

# Application Settings
REACT_APP_ENV=development
REACT_APP_LOG_LEVEL=debug
REACT_APP_THEME=light
```

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build locally
npm run preview

# Output will be in dist/ directory
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/           # Navigation and layout
│   │   ├── Dashboard/        # Home screen widgets
│   │   ├── Services/         # Service management
│   │   ├── System/           # System monitoring
│   │   ├── Agents/           # Agent management (placeholder)
│   │   ├── Knowledge/        # Knowledge base (placeholder)
│   │   └── common/           # Reusable components
│   ├── hooks/
│   │   ├── useWebSocket.js   # WebSocket connection
│   │   └── useAPI.js         # API calls hook
│   ├── services/
│   │   └── api.js            # API client configuration
│   ├── App.jsx               # Main app component
│   ├── index.jsx             # Entry point
│   └── theme.js              # Material-UI theme
├── public/                   # Static assets
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
└── package.json              # Dependencies
```

## API Integration

The frontend connects to the backend API at `http://localhost:54112` by default.

### Available API Endpoints

**System Monitoring:**
- `GET /api/system/stats` - System statistics (CPU, RAM, Disk)
- `GET /api/system/processes` - Running processes
- `GET /api/system/ports` - Port usage and process mapping

**Service Control:**
- `GET /api/services` - Service list and status
- `POST /api/services/{name}/start` - Start service
- `POST /api/services/{name}/stop` - Stop service
- `GET /api/services/{name}/logs` - Service logs
- `GET /api/services/{name}/status` - Service status

**Agent Management:**
- `GET /api/agents` - List all agents
- `GET /api/agents/summary` - Agent summary (tier breakdown)
- `GET /api/agents/{id}` - Agent details
- `POST /api/agents/{id}/invoke` - Invoke agent

**Knowledge Base:**
- `GET /api/knowledge/recent` - Recent knowledge files
- `GET /api/knowledge/search` - Search knowledge base
- `POST /api/knowledge/update` - Trigger update

**Health & Info:**
- `GET /health` - API health check
- `GET /docs` - API documentation (Swagger)

### WebSocket Real-time Updates

Connect to `ws://localhost:54112/api/system/ws` for real-time system updates:

```javascript
// Example WebSocket message
{
  "type": "system_stats",
  "timestamp": "2025-11-08T12:00:00Z",
  "cpu": { "usage": 45.2 },
  "memory": { "percent": 62.8 },
  "disk": { "percent": 71.3 }
}
```

### API Service Hooks

Use the provided hooks for API calls:

```javascript
// src/hooks/useAPI.js
import { useAPI } from './hooks/useAPI';

const MyComponent = () => {
  const { data, loading, error } = useAPI('/api/system/stats');
  return <div>{data?.cpu.usage}%</div>;
};
```

### Custom API Calls

Using axios directly:

```javascript
// src/services/api.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:54112';

export const getSystemStats = () => {
  return axios.get(`${API_URL}/api/system/stats`);
};
```

## Theme Customization

The app supports custom themes via `theme.json` in the public directory:

```json
{
  "primary": "#2196f3",
  "secondary": "#f50057",
  "success": "#4caf50",
  "warning": "#ff9800",
  "error": "#f44336",
  "info": "#2196f3"
}
```

## Features

### Dashboard

- **System Stats**: Real-time CPU, RAM, and disk usage with charts
- **Services Widget**: Quick service status and controls
- **Quick Actions**: One-click buttons for common tasks
- **Agent Summary**: Overview of agent hierarchy
- **Recent Knowledge**: Latest knowledge base updates

### Services Page

- **Service Cards**: Visual cards for each service
- **Start/Stop/Restart**: Service lifecycle management
- **Log Viewer**: Real-time log streaming with search
- **Auto-refresh**: Optional automatic status updates

### System Monitor

- **Live Charts**: CPU, RAM, disk usage over time
- **Process List**: Sortable, searchable process table
- **Port Scanner**: View all open ports and services
- **System Info**: Hardware and OS information

## Development Workflow

### Adding a New Page

1. Create component in `src/components/YourPage/`
```javascript
// src/components/YourPage/YourPage.jsx
import React from 'react';
import { Container, Paper } from '@mui/material';

export default function YourPage() {
  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Paper sx={{ p: 3 }}>
        <h1>Your Page</h1>
      </Paper>
    </Container>
  );
}
```

2. Add route in `src/App.jsx`
```javascript
import YourPage from './components/YourPage/YourPage';

<Route path="/your-page" element={<YourPage />} />
```

3. Add navigation item in `src/components/Layout/Navbar.jsx`
```javascript
<NavLink to="/your-page">Your Page</NavLink>
```

### Adding a New API Service

1. Create function in `src/services/api.js`
```javascript
export const getMyData = async () => {
  const response = await axios.get(`${API_URL}/api/my-endpoint`);
  return response.data;
};
```

2. Use in component with hook
```javascript
import { useEffect, useState } from 'react';
import { getMyData } from '../services/api';

export default function MyComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyData().then(setData).finally(() => setLoading(false));
  }, []);

  return loading ? <div>Loading...</div> : <div>{data}</div>;
}
```

### Styling Guidelines

- Use Material-UI components and theme
- Follow existing patterns for consistency
- Use `sx` prop for custom styling
- Maintain dark/light mode compatibility

### Component Best Practices

- Use functional components with hooks
- Keep components focused and reusable
- Prop validate with PropTypes or TypeScript
- Handle loading and error states
- Optimize performance with useMemo/useCallback

## Troubleshooting

### API Connection Failed

```bash
# Check backend is running
curl http://localhost:54112/health

# Verify .env configuration
cat .env

# Check browser console for CORS errors
# Backend CORS settings: check backend/config.py
```

### WebSocket Not Connecting

```bash
# Verify WebSocket URL in .env
REACT_APP_WS_URL=ws://localhost:54112

# Check browser DevTools Network tab for ws connections
# Ensure backend is running
docker-compose ps
```

### Port 3001 Already in Use

```bash
# Find process using port
netstat -ano | findstr :3001

# Kill process
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3002
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite

# Try building again
npm run build
```

### Hot Module Replacement (HMR) Issues

```bash
# Restart dev server
npm run dev

# Check Vite config for HMR settings
# May need to adjust for Docker environments
```

## Performance Optimization

### Code Splitting

Vite automatically code-splits at route boundaries. Use React.lazy for further optimization:

```javascript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Memoization

Use React.memo for expensive components:

```javascript
const MemoizedComponent = React.memo(function MyComponent(props) {
  return <div>{props.data}</div>;
});
```

## Deployment

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview build
npm run preview

# Check bundle size
npm run build -- --report
```

### Docker Production Build

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Dependencies

Key npm packages:
- **react** - UI library
- **react-dom** - React DOM rendering
- **@mui/material** - Component library
- **axios** - HTTP client
- **react-router-dom** - Routing
- **recharts** - Charting library

See `package.json` for complete list.

## Contributing

This frontend is part of the Ziggie Control Center project.

Guidelines:
1. Follow existing code patterns
2. Use TypeScript for new components
3. Write meaningful commit messages
4. Test changes before submitting
5. Update documentation as needed

## License

Part of Ziggie Control Center project. MIT License.

---

## Support & Resources

- **API Documentation:** http://localhost:54112/docs
- **Backend README:** `control-center/backend/README.md`
- **Main Project:** `README.md` in project root
- **Component Library:** Material-UI docs (https://mui.com)

---

**Ziggie Control Center Frontend**

*For development: `npm run dev`*
*For production: `npm run build && npm run preview`*
*Access at: http://localhost:3001*
