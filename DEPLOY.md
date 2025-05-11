# Kai-Sign Vercel Deployment Guide

This guide will help you set up and deploy the Kai-Sign application on Vercel.

## Local Development

To set up the project for local development:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Kai-Sign.git
   cd Kai-Sign
   ```

2. Set up the Python virtual environment:
   ```bash
   npm run setup-venv
   ```

3. Set the required environment variables:
   ```bash
   # For Linux/Mac
   export ETHERSCAN_API_KEY=your_etherscan_api_key

   # For Windows
   set ETHERSCAN_API_KEY=your_etherscan_api_key
   ```

   Or create a `.env` file in the root directory:
   ```
   ETHERSCAN_API_KEY=your_etherscan_api_key
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Visit `http://localhost:3000` to see the application.

## Vercel Deployment

To deploy the application to Vercel:

1. Make sure you have the Vercel CLI installed:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Set up environment variables in the Vercel project:
   - Go to your project settings in the Vercel dashboard
   - Add the following environment variables:
     - `ETHERSCAN_API_KEY`: Your Etherscan API key
   - Or use the Vercel CLI:
     ```bash
     vercel env add ETHERSCAN_API_KEY
     ```

4. Deploy the application:
   ```bash
   vercel
   ```

5. For production deployment:
   ```bash
   vercel --prod
   ```

## Important Configuration Files

- `vercel.json`: Configures how Vercel builds and routes the application
- `requirements.txt`: Lists Python dependencies
- `next.config.js`: Configures Next.js and API routes
- `api/index.py`: Main FastAPI application
- `api/healthcheck.py`: Simple health check endpoint
- `src/app/api/health/route.ts`: Next.js API health check

## Troubleshooting

If you encounter a 404 error on deployment:

1. Check that the erc7730 package is installed correctly:
   ```bash
   python test_erc7730.py
   ```

2. Verify the API endpoints:
   ```bash
   curl https://your-deployment-url.vercel.app/api/healthcheck
   curl https://your-deployment-url.vercel.app/api/health
   ```

3. Review the Vercel deployment logs for any errors.

If the API returns "contract source is not available on Etherscan":

1. Make sure the contract is verified on Etherscan
2. Check that you have set the `ETHERSCAN_API_KEY` environment variable correctly
3. Verify that your API key has permissions to access the contract data

## Post-Deployment Verification

After deploying, run the test script to verify the endpoints:

```bash
VERCEL_URL=your-deployment-url.vercel.app node test_deployment.js
```

This will check if all API endpoints are working correctly.

## Environment Variables

You need to set up the following environment variables in your Vercel project:

- `ETHERSCAN_API_KEY`: For accessing Etherscan API (required)
- Any other API keys or configuration variables needed by your application

Set them in the Vercel dashboard under Project Settings > Environment Variables. 