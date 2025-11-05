// Simple test script to verify AI integration
const testAIIntegration = async () => {
  try {
    console.log('Testing AI Integration...');
    
    // Get API URL from environment variables (consistent with other services)
    const apiUrl = process.env.REACT_APP_API_URL || process.env.REACT_APP_BACKEND_URL || '';
    const baseUrl = apiUrl || 'http://localhost:8000'; // Fallback only for test utility
    
    // Test the AI analytics endpoint
    const response = await fetch(`${baseUrl}/api/content-planning/ai-analytics/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ AI Integration Test Successful!');
    console.log('Response:', data);
    
    // Verify the response structure
    if (data.insights && data.recommendations) {
      console.log('✅ Response structure is correct');
      console.log(`📊 Found ${data.insights.length} insights`);
      console.log(`💡 Found ${data.recommendations.length} recommendations`);
    } else {
      console.log('⚠️ Response structure is missing expected fields');
    }
    
  } catch (error) {
    console.error('❌ AI Integration Test Failed:', error.message);
  }
};

// Run the test if this script is executed directly
if (typeof window === 'undefined') {
  // Node.js environment
  const fetch = require('node-fetch');
  testAIIntegration();
} else {
  // Browser environment
  window.testAIIntegration = testAIIntegration;
  console.log('AI Integration test function available as window.testAIIntegration()');
} 