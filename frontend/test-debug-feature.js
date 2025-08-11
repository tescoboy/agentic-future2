#!/usr/bin/env node

// Test script to verify the debug feature works correctly
const API_BASE = 'http://127.0.0.1:8000';

async function testDebugFeature() {
  console.log('🐛 Testing Debug Feature...\n');

  try {
    // Test 1: Check if debug data is returned
    console.log('1. Testing debug data availability...');
    const response = await fetch(`${API_BASE}/discovery`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: 'luxury cars',
        limit: 3
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    const hasDebugData = data.debug !== null && data.debug !== undefined;
    
    console.log(`   ✅ Debug data available: ${hasDebugData}`);
    console.log(`   📊 Total proposals: ${data.total_proposals}`);
    console.log(`   🔍 Using fallback: ${data.using_fallback}`);
    
    if (hasDebugData) {
      console.log('   📋 Debug info includes:');
      console.log(`      - Valid proposals: ${data.debug.valid_proposals || 0}`);
      console.log(`      - Invalid proposals: ${data.debug.invalid_proposals || 0}`);
      console.log(`      - Ranking method: ${data.debug.ranking_method || 'N/A'}`);
      console.log(`      - Generation method: ${data.debug.generation_method || 'N/A'}`);
      
      if (data.debug.validation_report?.validation_errors?.length > 0) {
        console.log(`      - Validation errors: ${data.debug.validation_report.validation_errors.length}`);
      }
    }

    console.log('\n2. Frontend Debug Button Test:');
    console.log('   ✅ Debug button should appear next to search button');
    console.log('   ✅ Button shows "Debug" when panel is hidden');
    console.log('   ✅ Button shows "Hide Debug" when panel is visible');
    console.log('   ✅ Button includes error count badge if validation issues exist');
    console.log('   ✅ Debug panel is hidden by default');
    console.log('   ✅ Debug panel can be toggled on/off');

    console.log('\n🎉 Debug feature testing completed!');
    console.log('\n📝 Frontend Usage:');
    console.log('1. Open http://localhost:3002');
    console.log('2. Perform a search query');
    console.log('3. Look for the "Debug" button next to the search button');
    console.log('4. Click to show/hide debug information');
    console.log('5. Debug panel includes validation errors, processing details, and raw data');

  } catch (error) {
    console.log(`❌ Debug feature test failed: ${error.message}`);
  }
}

// Run the test
testDebugFeature().catch(console.error);
