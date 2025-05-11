#!/bin/bash

# Exit on error
set -e

echo "Running build process for Vercel deployment..."

# Install Python dependencies directly (since Vercel will create a fresh environment)
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the Next.js app
echo "Building Next.js application..."
npm run build

echo "Build completed successfully!" 