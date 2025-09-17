#!/usr/bin/env python3
"""
Test script for Delivery Manager Web App
This script tests if all dependencies are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ Openpyxl imported successfully")
    except ImportError as e:
        print(f"❌ Openpyxl import failed: {e}")
        return False
    
    try:
        import reportlab
        print("✅ Reportlab imported successfully")
    except ImportError as e:
        print(f"❌ Reportlab import failed: {e}")
        return False
    
    return True

def test_app_file():
    """Test if the app.py file can be loaded"""
    print("\n🧪 Testing app.py...")
    
    if not os.path.exists("app.py"):
        print("❌ app.py not found!")
        return False
    
    try:
        # Try to compile the app
        with open("app.py", "r") as f:
            code = f.read()
        compile(code, "app.py", "exec")
        print("✅ app.py compiles successfully")
        return True
    except SyntaxError as e:
        print(f"❌ app.py has syntax errors: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading app.py: {e}")
        return False

def test_excel_file():
    """Test if Excel file can be read"""
    print("\n🧪 Testing Excel file...")
    
    if not os.path.exists("customers.xlsx"):
        print("ℹ️  customers.xlsx not found, will be created on first run")
        return True
    
    try:
        import pandas as pd
        df = pd.read_excel("customers.xlsx")
        print(f"✅ Excel file loaded successfully ({len(df)} rows)")
        return True
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

def main():
    print("🚚 Delivery Manager - Test Script")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed!")
        print("Please install missing packages:")
        print("pip install -r requirements_web.txt")
        return False
    
    # Test app file
    if not test_app_file():
        print("\n❌ App file test failed!")
        return False
    
    # Test Excel file
    if not test_excel_file():
        print("\n❌ Excel file test failed!")
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ The application should work correctly")
    print("\n🚀 You can now run:")
    print("- Windows: run_windows.bat")
    print("- Mac: ./run_mac.sh")
    print("- Linux: ./run_linux.sh")
    print("- Or: python launch.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
