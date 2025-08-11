# Signals Agent Frontend

React-based frontend for the Signals Agent platform, built with Vite, Bootstrap, and React Router.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Port Configuration

### Default Ports
- **Frontend**: 3000 (http://localhost:3000)
- **Backend**: 8000 (http://127.0.0.1:8000)

### Changing Ports

#### Frontend Port
You can change the frontend port in several ways:

1. **Environment Variable** (recommended):
   ```bash
   export VITE_PORT=3001
   npm run dev
   ```

2. **Environment File**:
   Create or edit `.env` file:
   ```
   VITE_PORT=3001
   VITE_API_BASE=http://127.0.0.1:8000
   ```

3. **Command Line**:
   ```bash
   VITE_PORT=3001 npm run dev
   ```

#### Backend Port
Update the API base URL in `.env`:
```
VITE_API_BASE=http://127.0.0.1:8001
```

### Port Fallback

The frontend automatically handles port conflicts:

- If port 3000 is busy, it will try 3001, 3002, etc.
- The chosen port is clearly displayed in the console
- No manual intervention required

## Development

### Scripts

- `npm run dev` - Start development server with health precheck
- `npm run dev:direct` - Start Vite directly (bypasses preflight check)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Health Precheck

The `predev` script automatically runs before starting the development server:

- Checks backend health at startup
- Provides helpful error messages if backend is down
- Shows configuration summary
- Continues startup even if backend is unavailable

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# Frontend Configuration
VITE_PORT=3000

# Backend Configuration
VITE_API_BASE=http://127.0.0.1:8000
```

## Troubleshooting

### Port 3000 is Already in Use

**Symptoms**: Error about port 3000 being busy

**Solutions**:
1. **Automatic**: The dev server will automatically choose the next available port
2. **Manual**: Set a specific port:
   ```bash
   VITE_PORT=3001 npm run dev
   ```
3. **Find and kill the process**:
   ```bash
   # Find what's using port 3000
   lsof -i :3000
   
   # Kill the process (replace PID with actual process ID)
   kill -9 PID
   ```

### Backend Connection Issues

**Symptoms**: Health check fails, API calls don't work

**Solutions**:
1. **Start the backend**:
   ```bash
   # In the signals-agent directory
   source .venv/bin/activate
   uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Check backend status**:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

3. **Verify API base URL**:
   - Check the API badge in the top-right corner of the UI
   - Verify `.env` file has correct `VITE_API_BASE`

### Development Server Won't Start

**Symptoms**: Vite fails to start

**Solutions**:
1. **Check Node.js version**:
   ```bash
   node --version  # Should be 18.x or higher
   ```

2. **Clear node_modules**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check for port conflicts**:
   ```bash
   lsof -i :3000
   ```

### Build Issues

**Symptoms**: `npm run build` fails

**Solutions**:
1. **Update dependencies**:
   ```bash
   npm update
   ```

2. **Clear cache**:
   ```bash
   npm run build -- --force
   ```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   ├── pages/              # Page components
│   ├── services/           # API and utility services
│   └── main.jsx           # Application entry point
├── scripts/
│   ├── dev.js             # Development server with port fallback
│   └── preflight.js       # Health check and preflight script
├── .env                   # Environment variables
├── package.json           # Dependencies and scripts
└── vite.config.js         # Vite configuration
```

## Features

- **Responsive Design**: Bootstrap-based responsive layout
- **Health Monitoring**: Automatic backend health checks
- **Port Fallback**: Automatic port selection if default is busy
- **Error Handling**: Comprehensive error UX with debug surfaces
- **Expandable Details**: Accordion-style data exploration
- **Real-time Status**: Status drawer for activation tracking

## API Integration

The frontend integrates with the Signals Agent backend API:

- **Discovery**: Search and discover signals
- **Activation**: Activate signals and proposals
- **Status**: Track activation status
- **Health**: Monitor backend health

All API calls include proper error handling and user feedback.

## Contributing

1. Follow the existing code style
2. Use Bootstrap components for UI
3. Include proper error handling
4. Test with both backend up and down
5. Update documentation for new features
