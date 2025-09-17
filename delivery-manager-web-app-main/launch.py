#!/usr/bin/env python3
"""
Simple launcher for Delivery Manager Web App
"""
import subprocess
import sys
import os

def main():
    print("🚚 Starting Delivery Manager Web Application...")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found!")
        print("Please run this script from the DeliveryManager_Web directory")
        input("Press Enter to exit...")
        return
    
    # Test imports first
    print("🧪 Testing dependencies...")
    try:
        import streamlit
        import pandas
        import openpyxl
        import reportlab
        print("✅ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"], check=True)
            print("✅ Requirements installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            input("Press Enter to exit...")
            return
    
    try:
        # Start streamlit with better error handling
        print("🚀 Starting web application...")
        print("The app will open at: http://localhost:8501")
        print("Press Ctrl+C to stop the application")
        print("-" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501",
            "--server.runOnSave", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        print("Try running: python test_app.py to diagnose issues")
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()