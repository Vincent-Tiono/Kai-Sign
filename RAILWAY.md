# Kai-Sign Railway Deployment Guide

This guide will help you deploy the Kai-Sign application on Railway.

## Prerequisites

- A [Railway account](https://railway.app/)
- Git
- The Railway CLI (optional)

## Deployment Steps

### Option 1: Deploy via Dashboard

1. Log in to your Railway account and create a new project
2. Choose "Deploy from GitHub repo"
3. Select the Kai-Sign repository
4. Choose the commit f59932c or fork from it
5. Set the required environment variables:
   - `ETHERSCAN_API_KEY`: Your Etherscan API key
6. Railway will automatically detect the configuration in `railway.json` and deploy the application

### Option 2: Deploy via CLI

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to your Railway project:
   ```bash
   railway link
   ```

4. Set the required environment variables:
   ```bash
   railway variables set ETHERSCAN_API_KEY=your_etherscan_api_key
   ```

5. Deploy the application:
   ```bash
   railway up
   ```

## Configuration Files

- `railway.json`: Configuration for Railway deployment
- `Procfile`: Process definition for web servers
- `requirements.txt`: Python dependencies

## Testing

Before deploying to Railway, test the API locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   uvicorn api.index:app --reload
   ```

3. Run the test script:
   ```bash
   python test_railway.py
   ```

## Troubleshooting

If you encounter issues with the deployment:

1. Check the Railway deployment logs
2. Verify that all environment variables are set correctly
3. Make sure the contract addresses you're using are verified on Etherscan
4. Check that your Etherscan API key has the necessary permissions 