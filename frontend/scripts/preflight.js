#!/usr/bin/env node

import axios from 'axios';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the directory of the current script
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from .env file
const envPath = join(__dirname, '..', '.env');
let envVars = {};

try {
  const envContent = await import('fs').then(fs => fs.readFileSync(envPath, 'utf8'));
  envContent.split('\n').forEach(line => {
    const [key, ...valueParts] = line.split('=');
    if (key && valueParts.length > 0) {
      envVars[key.trim()] = valueParts.join('=').trim();
    }
  });
} catch (error) {
  // .env file doesn't exist or can't be read, use defaults
}

// Get API base URL from environment or use default
const apiBaseUrl = process.env.VITE_API_BASE || envVars.VITE_API_BASE || 'http://127.0.0.1:8000';

console.log('🚀 Signals Agent Frontend - Preflight Check');
console.log('==========================================');
console.log('');

// Check backend health
async function checkBackendHealth() {
  console.log(`🔍 Checking backend health at: ${apiBaseUrl}/health`);
  
  try {
    const response = await axios.get(`${apiBaseUrl}/health`, {
      timeout: 5000,
      validateStatus: () => true // Don't throw on any status code
    });
    
    if (response.status === 200 && response.data?.ok) {
      console.log('✅ Backend is healthy and ready');
      console.log(`   Mode: ${response.data.mode || 'unknown'}`);
      console.log(`   Version: ${response.data.version || 'unknown'}`);
      return true;
    } else {
      console.log('⚠️  Backend responded but may have issues');
      console.log(`   Status: ${response.status}`);
      console.log(`   Response: ${JSON.stringify(response.data)}`);
      return false;
    }
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ Backend is not running');
      console.log('');
      console.log('💡 To start the backend:');
      console.log('   1. Open a new terminal');
      console.log('   2. Navigate to the signals-agent directory');
      console.log('   3. Run: source .venv/bin/activate');
      console.log('   4. Run: uvicorn simple_app:app --host 127.0.0.1 --port 8000 --reload');
      console.log('');
      console.log('   Or use the manage_servers.sh script:');
      console.log('   ./manage_servers.sh start');
      console.log('');
    } else if (error.code === 'ENOTFOUND') {
      console.log('❌ Cannot resolve backend hostname');
      console.log(`   Check your VITE_API_BASE setting: ${apiBaseUrl}`);
      console.log('');
    } else if (error.code === 'ETIMEDOUT') {
      console.log('❌ Backend health check timed out');
      console.log('   Backend may be starting up or overloaded');
      console.log('');
    } else {
      console.log('❌ Backend health check failed');
      console.log(`   Error: ${error.message}`);
      console.log('');
    }
    
    console.log('⚠️  Frontend will start anyway, but backend features may not work');
    console.log('');
    return false;
  }
}

// Main preflight function
async function preflight() {
  const isHealthy = await checkBackendHealth();
  
  console.log('📋 Environment Configuration:');
  console.log(`   Frontend Port: ${envVars.VITE_PORT || process.env.VITE_PORT || '3000'}`);
  console.log(`   API Base URL: ${apiBaseUrl}`);
  console.log('');
  
  if (!isHealthy) {
    console.log('🚨 Backend Health Issues Detected');
    console.log('   The frontend will start, but you may experience:');
    console.log('   - Discovery searches will fail');
    console.log('   - Activation requests will fail');
    console.log('   - Status checks will fail');
    console.log('');
    console.log('   Start the backend first for full functionality.');
    console.log('');
  }
  
  console.log('🎯 Starting frontend development server...');
  console.log('');
}

// Run preflight check
preflight().catch(error => {
  console.error('❌ Preflight check failed:', error.message);
  console.log('');
  console.log('🚀 Starting frontend anyway...');
  console.log('');
});
