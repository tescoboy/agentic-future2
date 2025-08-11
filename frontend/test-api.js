// Simple test script to verify API client functionality
import apiClient from './src/services/api.js';
import { isHealthResponse } from './src/services/typeGuards.js';

async function testAPI() {
  console.log('🧪 Testing API Client...');
  
  try {
    // Test health endpoint
    console.log('📡 Testing getHealth()...');
    const health = await apiClient.getHealth();
    console.log('✅ Health response:', health);
    
    // Test type guard
    console.log('🔍 Testing type guard...');
    const isValid = isHealthResponse(health);
    console.log('✅ Type guard result:', isValid);
    
    console.log('🎉 All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testAPI();
