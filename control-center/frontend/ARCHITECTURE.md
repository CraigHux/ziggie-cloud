# Control Center Frontend Architecture

## Overview

The Control Center frontend is a React-based single-page application (SPA) that provides a modern web interface for managing the entire Meow Ping RTS development ecosystem.

## Architecture Principles

1. **Component-Based**: Modular, reusable React components
2. **Real-Time Updates**: WebSocket integration for live data
3. **API-First**: Clean separation between frontend and backend
4. **Responsive Design**: Desktop-first with mobile support
5. **Theme Support**: Dark/light mode with customizable themes

## Technology Stack

### Core
- **React 18**: Modern React with functional components and hooks
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing

### UI Framework
- **Material-UI v5**: Comprehensive component library
- **Emotion**: CSS-in-JS styling
- **Recharts**: Data visualization and charts

### Data Management
- **Axios**: HTTP client for API calls
- **WebSocket API**: Native WebSocket for real-time updates
- **Custom Hooks**: Reusable logic for API and WebSocket

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Layout/          # App layout and navigation
│   │   ├── Dashboard/       # Home dashboard widgets
│   │   ├── Services/        # Service management
│   │   ├── System/          # System monitoring
│   │   ├── Agents/          # Agent management (future)
│   │   ├── Knowledge/       # Knowledge base (future)
│   │   └── common/          # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   │   ├── useAPI.js       # API call hook
│   │   └── useWebSocket.js # WebSocket hook
│   ├── services/            # API client
│   │   └── api.js          # Axios configuration
│   ├── App.jsx              # Main app component
│   ├── index.jsx            # Entry point
│   └── theme.js             # MUI theme configuration
├── public/                  # Static assets
├── index.html               # HTML template
└── vite.config.js           # Vite configuration
```

## Component Hierarchy

```
App
├── ThemeProvider (Material-UI)
├── CssBaseline
└── Router
    └── Layout
        ├── Navbar (with Drawer)
        ├── Main Content
        │   └── Routes
        │       ├── Dashboard
        │       │   ├── SystemStats
        │       │   ├── ServicesWidget
        │       │   ├── QuickActions
        │       │   └── RecentActivity
        │       ├── ServicesPage
        │       │   ├── ServiceCard (multiple)
        │       │   └── LogViewer (dialog)
        │       ├── SystemPage
        │       │   ├── SystemStats
        │       │   ├── ProcessList
        │       │   └── PortScanner
        │       ├── AgentsPage (placeholder)
        │       └── KnowledgePage (placeholder)
        └── Footer
```

## Data Flow

### API Communication

```
Component → useAPI Hook → Axios → Backend API
                ↓
         State Update → Re-render
```

### WebSocket Updates

```
WebSocket Server → useWebSocket Hook → Callback
                                          ↓
                                    State Update → Re-render
```

### State Management

- **Local State**: `useState` for component-specific data
- **Context**: None currently (can add if needed)
- **Props**: Parent-child communication
- **Custom Hooks**: Shared logic and data fetching

## Key Features

### 1. Dashboard

**Purpose**: Main overview screen with key metrics and quick actions

**Components**:
- `SystemStats`: CPU, RAM, disk usage with charts
- `ServicesWidget`: Service status with controls
- `QuickActions`: One-click action buttons
- `RecentActivity`: Activity log

**Data Sources**:
- WebSocket: Real-time system stats
- API: Services, agents, knowledge base

### 2. Services Management

**Purpose**: Manage all backend services

**Components**:
- `ServicesPage`: Main service list
- `ServiceCard`: Individual service display
- `LogViewer`: Real-time log viewer

**Features**:
- Start/Stop/Restart services
- View real-time logs
- Search and filter services
- Auto-refresh status

### 3. System Monitor

**Purpose**: Monitor system resources and processes

**Components**:
- `SystemPage`: Main system view
- `SystemStats`: Resource usage charts
- `ProcessList`: Running processes table
- `PortScanner`: Open ports table

**Features**:
- Live system metrics
- Sortable, searchable tables
- Process and port information

### 4. Real-Time Updates

**WebSocket Integration**:
- Automatic connection on app load
- Reconnection with exponential backoff
- Connection status indicator
- Message parsing and routing

**Message Format**:
```json
{
  "type": "system_stats",
  "cpu": { "usage": 45.2 },
  "memory": { "percent": 62.8 },
  "disk": { "percent": 71.3 }
}
```

## Custom Hooks

### useAPI

**Purpose**: Simplified API calls with loading and error states

```javascript
const { data, loading, error, refetch } = useAPI(apiFunction, dependencies, autoFetch);
```

**Features**:
- Automatic loading state
- Error handling
- Manual refetch
- Auto-fetch on mount

### useWebSocket

**Purpose**: WebSocket connection management

```javascript
const { isConnected, error, send, reconnect } = useWebSocket(onMessage);
```

**Features**:
- Automatic connection
- Auto-reconnect with backoff
- Message handler callback
- Connection status

## Theming

### Default Theme

- Dark mode by default
- Material-UI theme customization
- Consistent color palette
- Custom component styles

### Theme Customization

Place `theme.json` in `public/` directory:

```json
{
  "primary": "#2196f3",
  "secondary": "#f50057",
  "success": "#4caf50",
  "warning": "#ff9800",
  "error": "#f44336"
}
```

### Dark/Light Mode

Toggle button in navbar switches between modes. Theme is recreated with new palette.

## API Integration

### Base Configuration

- Base URL: `http://localhost:8080/api`
- Timeout: 10 seconds
- Content-Type: `application/json`

### Interceptors

**Request**:
- Add auth token if available
- Log requests in dev mode

**Response**:
- Parse response data
- Handle errors globally
- Log errors in dev mode

### API Modules

- `systemAPI`: System information
- `servicesAPI`: Service management
- `agentsAPI`: Agent information
- `knowledgeAPI`: Knowledge base
- `apiUsageAPI`: API usage stats

## Error Handling

### API Errors

- Try-catch in components
- Error state in hooks
- User-friendly error messages
- Toast notifications (Snackbar)

### WebSocket Errors

- Connection error indicator
- Auto-reconnect logic
- Error state in hook
- User notification

## Performance Optimizations

1. **Code Splitting**: React Router lazy loading (can be added)
2. **Memoization**: `React.memo` for expensive components
3. **Virtual Scrolling**: For long lists (can be added)
4. **Debouncing**: Search inputs
5. **Chart Optimization**: Limited data points (30 max)

## Future Enhancements

### Planned Features

1. **Agent Management**: Full L1/L2/L3 agent interface
2. **Knowledge Base**: Document viewer and search
3. **Settings Page**: User preferences
4. **Authentication**: Login and user management
5. **Notifications**: Push notifications
6. **Themes**: More theme options
7. **Mobile App**: React Native version

### Technical Improvements

1. **TypeScript**: Add type safety
2. **Testing**: Jest + React Testing Library
3. **State Management**: Redux/Zustand if needed
4. **PWA**: Progressive Web App features
5. **Offline Mode**: Service Worker
6. **Performance**: Further optimizations

## Development Workflow

### Local Development

```bash
npm run dev    # Start dev server
npm run build  # Build for production
npm run preview # Preview production build
npm run lint   # Run ESLint
```

### Adding New Features

1. Create component in appropriate directory
2. Add to routing if needed
3. Create API methods if needed
4. Update navigation if needed
5. Test thoroughly

### Code Style

- Functional components with hooks
- PropTypes or TypeScript for props
- Clean, commented code
- Consistent naming conventions
- Material-UI components preferred

## Deployment

### Build Process

```bash
npm run build
```

Outputs to `dist/` directory.

### Environment Variables

- `VITE_API_URL`: Backend API URL
- `VITE_WS_URL`: WebSocket URL
- `VITE_DEV_MODE`: Development mode flag

### Hosting Options

- Static hosting (Vercel, Netlify, etc.)
- Docker container
- Node.js server (Express)
- Integrated with backend

## Integration Points

### Backend API

Frontend expects these endpoints:

- `GET /api/system/stats`
- `GET /api/system/processes`
- `GET /api/system/ports`
- `GET /api/services`
- `POST /api/services/:name/start`
- `POST /api/services/:name/stop`
- `GET /api/services/:name/logs`
- `GET /api/agents/summary`
- `GET /api/knowledge/recent`

### WebSocket Server

- URL: `ws://localhost:8080/ws/system`
- Protocol: JSON messages
- Types: `system_stats`, `service_update`, etc.

### Art Director

Receives `theme.json` with color scheme for theming.

## Maintenance

### Regular Updates

- Update dependencies monthly
- Monitor security advisories
- Update React and MUI versions
- Test after updates

### Monitoring

- Browser console errors
- API error rates
- WebSocket connection status
- User feedback

## Conclusion

The Control Center frontend provides a modern, responsive interface for managing the Meow Ping RTS ecosystem. Built with React and Material-UI, it emphasizes real-time updates, clean code, and great user experience.
