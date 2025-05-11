// @ts-nocheck
import fetch from 'node-fetch';

// Replace with your actual Vercel deployment URL
const VERCEL_URL = process.env.VERCEL_URL || 'https://your-vercel-deployment-url.vercel.app';

async function testEndpoint(path, name) {
  try {
    console.log(`Testing ${name} at ${path}...`);
    const response = await fetch(`${VERCEL_URL}${path}`);
    const status = response.status;
    const body = await response.text();
    
    console.log(`Status: ${status}`);
    console.log(`Response: ${body.substring(0, 200)}${body.length > 200 ? '...' : ''}`);
    
    if (status >= 200 && status < 300) {
      console.log(`✅ ${name} test passed`);
    } else {
      console.log(`❌ ${name} test failed`);
    }
  } catch (error) {
    console.log(`❌ ${name} test error: ${error.message}`);
  }
  console.log('-----------------------------------');
}

async function runTests() {
  console.log(`Testing Vercel deployment at ${VERCEL_URL}`);
  console.log('===================================');
  
  // Test Next.js API route
  await testEndpoint('/api/health', 'Next.js API Health');
  
  // Test Python serverless function
  await testEndpoint('/api/healthcheck', 'Python API Healthcheck');
  
  // Test main API endpoint (just test the endpoint exists, not functionality)
  await testEndpoint('/api/py/generateERC7730', 'Main API route');
  
  console.log('All tests completed');
}

runTests().catch(console.error); 