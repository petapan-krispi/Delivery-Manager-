#!/bin/bash

echo "========================================"
echo "   Delivery Manager - Web Application"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python using your package manager:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "✅ Python3 found"
echo

# Check if requirements are installed
echo "📦 Installing/updating required packages..."
pip3 install -r requirements_web.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages"
    echo "Trying with --user flag..."
    pip3 install -r requirements_web.txt --user --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Still failed. Please check your internet connection"
        exit 1
    fi
fi

echo "✅ Packages installed successfully"
echo

# Start the web application
echo "🚀 Starting Delivery Manager..."
echo
echo "The application will open in your default web browser."
echo "If it doesn't open automatically, go to: http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

streamlit run app.py --server.port 8501 --server.headless true --server.runOnSave true --server.enableCORS false --server.enableXsrfProtection false
