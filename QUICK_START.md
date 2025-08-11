# 🚀 Signals Agent Quick Start Guide

## ⚠️ **IMPORTANT: Directory Confusion Fix**

**Problem**: Running `npm run dev` from the wrong directory causes "package.json not found" errors.

**Solution**: Use these scripts from ANY directory!

## 🎯 **Easy Startup Commands**

### Option 1: Use the Convenience Scripts (Recommended)

```bash
# Start Backend (Terminal 1)
./start-backend.sh

# Start Frontend (Terminal 2)  
./start-frontend.sh
```

### Option 2: Manual Commands (If you prefer)

```bash
# Backend (Terminal 1)
cd signals-agent
source .venv/bin/activate
uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload

# Frontend (Terminal 2)
cd frontend
npm run dev:direct
```

## 🌐 **Working URLs**

- **Frontend**: http://localhost:3000
- **Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 🔧 **Troubleshooting**

### If you get "package.json not found":
1. **Don't run npm from the root directory**
2. **Use the scripts**: `./start-frontend.sh`
3. **Or navigate properly**: `cd frontend && npm run dev:direct`

### If ports are busy:
- Frontend will automatically choose port 3001, 3002, etc.
- Check the console output for the actual port

### If backend won't start:
- Make sure you're in the right directory: `cd signals-agent`
- Activate virtual environment: `source .venv/bin/activate`

## 📁 **Directory Structure**

```
agentic-future2/
├── start-frontend.sh      # ✅ Use this to start frontend
├── start-backend.sh       # ✅ Use this to start backend
├── signals-agent/         # Backend code
└── frontend/             # Frontend code
```

## 🎉 **Success Indicators**

- **Backend**: Shows "INFO: Application startup complete"
- **Frontend**: Shows "VITE v5.4.19 ready" and "Local: http://localhost:3000/"
- **Health Check**: `curl http://127.0.0.1:8000/health` returns `{"ok":true}`

## 💡 **Pro Tips**

1. **Always use the scripts** - they handle directory navigation automatically
2. **Check the console output** - it tells you exactly what's happening
3. **Use two terminal windows** - one for backend, one for frontend
4. **Bookmark the URLs** - http://localhost:3000 and http://127.0.0.1:8000/docs

## 🚨 **Common Mistakes to Avoid**

❌ **Don't run from root directory**:
```bash
# WRONG - This will fail
cd /Users/harvingupta/Documents/agentic-future-2/agentic-future2
npm run dev
```

✅ **Do use the scripts**:
```bash
# RIGHT - This will work from anywhere
./start-frontend.sh
```
