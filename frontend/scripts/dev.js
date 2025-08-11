#!/usr/bin/env node

import { spawn } from 'child_process';
import { createServer } from 'net';

// Function to check if a port is available
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = createServer();
    server.listen(port, () => {
      server.once('close', () => {
        resolve(true);
      });
      server.close();
    });
    server.on('error', () => {
      resolve(false);
    });
  });
}

// Function to find the next available port
async function findAvailablePort(startPort) {
  let port = startPort;
  while (!(await isPortAvailable(port))) {
    port++;
  }
  return port;
}

// Main function
async function main() {
  const startPort = parseInt(process.env.VITE_PORT) || 3000;
  
  const availablePort = await findAvailablePort(startPort);
  
  // Load environment variables from .env file
  const { fileURLToPath } = await import('url');
  const { dirname, join } = await import('path');
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
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
  
  const apiBaseUrl = envVars.VITE_API_BASE || process.env.VITE_API_BASE || 'http://127.0.0.1:8000';
  
  console.log('🎯 Frontend Development Server Starting...');
  console.log('==========================================');
  console.log('');
  
  if (availablePort !== startPort) {
    console.log(`⚠️  Port ${startPort} is busy, using port ${availablePort} instead`);
  } else {
    console.log(`✅ Starting on port ${availablePort}`);
  }
  
  console.log('');
  console.log('🌐 URLs:');
  console.log(`   Frontend: http://localhost:${availablePort}`);
  console.log(`   Backend:  ${apiBaseUrl}`);
  console.log('');
  console.log('📋 Configuration:');
  console.log(`   Frontend Port: ${availablePort}`);
  console.log(`   API Base URL: ${apiBaseUrl}`);
  console.log('');
  
  // Set the port environment variable for Vite
  process.env.VITE_DEV_PORT = availablePort;
  
  // Start Vite with the available port
  const vite = spawn('npx', ['vite', '--port', availablePort], {
    stdio: 'inherit',
    env: { ...process.env, PORT: availablePort }
  });
  
  vite.on('error', (error) => {
    console.error('❌ Failed to start Vite:', error);
    process.exit(1);
  });
  
  vite.on('close', (code) => {
    console.log(`\n👋 Frontend server stopped with code ${code}`);
    process.exit(code);
  });
}

main().catch(console.error);
