#!/bin/bash

echo "Starting InternGenius Application..."
echo ""
echo "Please wait while we set up the environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Start the application
echo ""
echo "Starting the application..."
python simple_app.py

echo ""
read -p "Press [Enter] key to exit..."
