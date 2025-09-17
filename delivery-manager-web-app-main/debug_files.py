#!/usr/bin/env python3
"""
Debug script to check file paths and Excel file loading in Streamlit Cloud.
Run this to troubleshoot Excel file loading issues.
"""

import os
import sys

def debug_file_paths():
    """Debug file paths and Excel file availability."""
    print("=== File Path Debug Information ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    print("\n=== Files in current directory ===")
    try:
        files = os.listdir('.')
        for file in sorted(files):
            print(f"  - {file}")
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    print("\n=== Files in parent directory ===")
    try:
        parent_files = os.listdir('..')
        for file in sorted(parent_files):
            print(f"  - {file}")
    except Exception as e:
        print(f"Error listing parent directory: {e}")
    
    print("\n=== Excel file checks ===")
    excel_files = [
        "business_excel.xlsx",
        "customers.xlsx",
        os.path.join("..", "business_excel.xlsx"),
        os.path.join("..", "customers.xlsx")
    ]
    
    for excel_file in excel_files:
        exists = os.path.exists(excel_file)
        print(f"  - {excel_file}: {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            try:
                size = os.path.getsize(excel_file)
                print(f"    Size: {size} bytes")
            except Exception as e:
                print(f"    Error getting size: {e}")

if __name__ == "__main__":
    debug_file_paths()
