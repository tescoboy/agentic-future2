# Backend Deployment Guide

## 🚀 **Quick Deploy Options**

### **Option 1: Railway (Recommended - Easiest)**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `agentic-future2` repository
5. Railway will auto-detect it's a Python app
6. Add environment variable: `GOOGLE_API_KEY=your_key`
7. Deploy!

### **Option 2: Render**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your `agentic-future2` repository
5. Set build command: `cd signals-agent && pip install -r ../requirements.txt`
6. Set start command: `cd signals-agent && uvicorn simple_app:app --host 0.0.0.0 --port $PORT`
7. Add environment variable: `GOOGLE_API_KEY=your_key`

### **Option 3: Heroku**
```bash
heroku create your-app-name
heroku config:set GOOGLE_API_KEY=your_key
git push heroku main
```

## 🔧 **After Backend Deployment**

1. **Get your backend URL** (e.g., `https://your-app.railway.app`)
2. **Update frontend environment**:
   ```bash
   cd frontend
   # Edit .env file to change:
   VITE_API_BASE=https://your-backend-url.railway.app
   ```
3. **Redeploy frontend** to Vercel (or it will auto-deploy)

## ✅ **Files Ready for Deployment**
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Heroku configuration
- ✅ `runtime.txt` - Python version
- ✅ `signals-agent/` - Backend code

## 🎯 **Current Status**
- ✅ **Frontend**: Deployed on Vercel
- ❌ **Backend**: Needs deployment
- ✅ **All files**: Ready for deployment
