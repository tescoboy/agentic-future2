#!/usr/bin/env node

// Test script to verify the limit feature works correctly
const API_BASE = 'http://127.0.0.1:8000';

async function testLimitFeature() {
  console.log('🧪 Testing Limit Feature...\n');

  const testCases = [
    { limit: undefined, expected: 5, description: 'Default limit (no limit specified)' },
    { limit: 1, expected: 1, description: 'Minimum limit' },
    { limit: 3, expected: 3, description: 'Custom limit' },
    { limit: 5, expected: 5, description: 'Default limit (explicit)' },
    { limit: 8, expected: 8, description: 'Custom limit' },
    { limit: 10, expected: 10, description: 'Maximum limit' },
    { limit: 15, expected: 10, description: 'Limit above max (should be capped)' }
  ];

  for (const testCase of testCases) {
    try {
      const requestBody = {
        query: 'luxury cars',
        ...(testCase.limit && { limit: testCase.limit })
      };

      const response = await fetch(`${API_BASE}/discovery`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const actualProposals = data.total_proposals;
      const passed = actualProposals === testCase.expected;

      console.log(`${passed ? '✅' : '❌'} ${testCase.description}`);
      console.log(`   Requested: ${testCase.limit || 'default'}, Got: ${actualProposals}, Expected: ${testCase.expected}`);
      
      if (!passed) {
        console.log(`   ❌ FAILED: Expected ${testCase.expected} but got ${actualProposals}`);
      }
      console.log('');

    } catch (error) {
      console.log(`❌ ${testCase.description} - ERROR: ${error.message}\n`);
    }
  }

  console.log('🎉 Limit feature testing completed!');
  console.log('\n📝 Frontend Usage:');
  console.log('1. Open http://localhost:3000');
  console.log('2. Use the "Response Limit" dropdown to select 1-10 proposals');
  console.log('3. Default is 5 proposals');
  console.log('4. Maximum is 10 proposals');
}

// Run the test
testLimitFeature().catch(console.error);
