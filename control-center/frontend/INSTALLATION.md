# Installation Guide

Quick setup guide for the Control Center Frontend.

## Prerequisites

- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- **npm**: Comes with Node.js
- **Backend API**: Running on `http://localhost:8080`

## Quick Start

### 1. Install Dependencies

```bash
cd C:\meowping-rts\control-center\frontend
npm install
```

This will install all required packages:
- React 18
- Material-UI 5
- React Router
- Axios
- Recharts
- Vite

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env if needed (default values should work)
```

Default configuration:
```
VITE_API_URL=http://localhost:8080/api
VITE_WS_URL=ws://localhost:8080/ws/system
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at: `http://localhost:3000`

### 4. Verify Backend Connection

The dashboard should connect to:
- API: `http://localhost:8080/api`
- WebSocket: `ws://localhost:8080/ws/system`

Check the navbar for connection status indicator.

## Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

Build output: `dist/` directory

## Troubleshooting

### Installation Issues

**Problem**: `npm install` fails

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete existing files
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Port Already in Use

**Problem**: Port 3000 is already in use

**Solution**: Change port in `vite.config.js`:
```javascript
server: {
  port: 3001, // Change to any available port
}
```

### API Connection Failed

**Problem**: Cannot connect to backend API

**Solutions**:
1. Verify backend is running: `http://localhost:8080/api/health`
2. Check CORS settings in backend
3. Verify `.env` file has correct API URL
4. Check browser console for errors

### WebSocket Not Connecting

**Problem**: Real-time updates not working

**Solutions**:
1. Verify WebSocket server is running
2. Check WebSocket URL in `.env`
3. Look for connection errors in browser console
4. Verify firewall is not blocking WebSocket

### Build Errors

**Problem**: Build fails with errors

**Solutions**:
1. Check Node.js version: `node --version` (should be 18+)
2. Clear cache: `npm cache clean --force`
3. Remove and reinstall: `rm -rf node_modules && npm install`
4. Check for ESLint errors: `npm run lint`

## Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes to code will appear immediately without full reload.

### Browser DevTools

- **React DevTools**: Install browser extension for component inspection
- **Console**: Check for errors and warnings
- **Network**: Monitor API calls and WebSocket

### Code Linting

```bash
# Run ESLint
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

## File Structure

After installation, you should have:

```
frontend/
├── node_modules/         # Dependencies (don't commit)
├── public/               # Static assets
│   └── theme.json       # Theme configuration
├── src/                  # Source code
│   ├── components/      # React components
│   ├── hooks/           # Custom hooks
│   ├── services/        # API client
│   ├── App.jsx          # Main app
│   ├── index.jsx        # Entry point
│   └── theme.js         # Theme config
├── .env                  # Environment variables (don't commit)
├── .eslintrc.json       # ESLint config
├── .gitignore           # Git ignore
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.js       # Vite config
└── README.md            # Documentation
```

## Next Steps

1. **Customize Theme**: Edit `public/theme.json`
2. **Configure API**: Update `.env` if backend URL differs
3. **Add Features**: Start building new components
4. **Test**: Verify all pages work correctly

## Support

For issues or questions:
1. Check browser console for errors
2. Verify backend is running
3. Review README.md for detailed docs
4. Check ARCHITECTURE.md for technical details

## Common Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build production
npm run preview          # Preview production build
npm run lint             # Lint code

# Dependencies
npm install              # Install dependencies
npm update               # Update dependencies
npm outdated             # Check for outdated packages
```

## Production Deployment

### Option 1: Static Hosting

```bash
npm run build
# Upload dist/ folder to static host (Vercel, Netlify, etc.)
```

### Option 2: Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Option 3: Node.js Server

Use the built-in preview server or serve with Express.

## Environment Variables

### Development

- `VITE_API_URL`: Backend API base URL
- `VITE_WS_URL`: WebSocket server URL
- `VITE_DEV_MODE`: Enable dev features

### Production

Set these in your hosting platform or `.env.production`.

## Security Notes

- Don't commit `.env` files
- Use environment variables for secrets
- Enable HTTPS in production
- Validate all API responses
- Sanitize user inputs

## Performance

The app is optimized for performance:
- Vite's fast build and HMR
- Lazy loading (can be added)
- Efficient re-renders
- WebSocket for real-time data
- Optimized charts (limited data points)

## Conclusion

You should now have a working Control Center frontend! If you encounter issues, check the troubleshooting section or consult the detailed documentation.
