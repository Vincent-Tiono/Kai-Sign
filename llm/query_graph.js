import { request, gql } from 'graphql-request';
import fs from 'fs';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

// Get current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Get contract address from deployment.json
let contractAddress;
try {
  const deploymentPath = new URL('../deployment.json', import.meta.url);
  const deploymentData = JSON.parse(fs.readFileSync(deploymentPath, 'utf8'));
  contractAddress = deploymentData.kaisignContract;
} catch (error) {
  console.error('Error reading deployment.json:', error);
  process.exit(1);
}

if (!contractAddress) {
  console.error('Error: kaisignContract not found in deployment.json');
  process.exit(1);
}

console.log(`Using contract address: ${contractAddress}`);

// API key for The Graph
const apiKey = "be5ddfca879e5ea553aa90060c35999a";
console.log(`Using API key: ${apiKey}`);

// The Graph API endpoint with API key in the URL path
const endpoint = `https://gateway.thegraph.com/api/${apiKey}/subgraphs/id/F3XjWNiNFUTbZhNQjXuhP7oDug2NaPwMPZ5XCRx46h5U`;
console.log(`Endpoint: ${endpoint}`);

const query = gql`{
  questions(where: {user: "${contractAddress}"}) 
  {
    data
  }
}`;

// No need for Authorization header as API key is in the URL
const headers = {
  "Content-Type": "application/json"
};

async function fetchData() {
  try {
    console.log('Querying The Graph API...');
    const data = await request(endpoint, query, {}, headers);
    
    console.log('\nAPI Response:');
    console.log(JSON.stringify(data, null, 2));
    
    if (data.questions && data.questions.length > 0) {
      console.log(`\nFound ${data.questions.length} questions.`);
      
      // Create directory for saving specs
      const specsDir = new URL('./specs', import.meta.url);
      try {
        fs.mkdirSync(specsDir, { recursive: true });
      } catch (error) {
        // Directory might already exist
      }
      
      // Process each IPFS hash
      data.questions.forEach((question, index) => {
        const ipfsHash = question.data;
        console.log(`\nIPFS Hash ${index + 1}/${data.questions.length}: ${ipfsHash}`);
        
        // Save IPFS hash to a file for later processing with hash_prob.py
        const hashFilePath = new URL(`./specs/ipfs_hash_${index + 1}.txt`, import.meta.url);
        fs.writeFileSync(hashFilePath, ipfsHash);
      });
      
      console.log('\nTo evaluate a specific IPFS hash, run:');
      console.log('python hash_prob.py <ipfs_hash>');
    } else {
      console.log('\nNo questions found for this contract address.');
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    if (error.response) {
      console.error('Response details:', JSON.stringify(error.response, null, 2));
    }
  }
}

fetchData(); 