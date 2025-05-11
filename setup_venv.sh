#!/bin/bash

# Exit on error
set -e

echo "Setting up Python virtual environment..."

# Find the best Python version available
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD=python3.10
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD=python3.9
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "Error: No suitable Python version found."
    exit 1
fi

echo "Using $PYTHON_CMD version:"
$PYTHON_CMD --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  $PYTHON_CMD -m venv venv
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Make sure pip is up-to-date
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Setup complete! To activate the virtual environment, run:"
echo "source venv/bin/activate" 