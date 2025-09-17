🚚 DELIVERY MANAGER - WEB APPLICATION
=====================================

A cross-platform web-based delivery management system that runs in your browser.

📋 FEATURES:
- ✅ Add, Edit, Delete customers
- ✅ Search and filter customers
- ✅ Print delivery labels (PDF)
- ✅ Export data to Excel
- ✅ Works on Windows, Mac, Linux
- ✅ No installation required (just Python)

🚀 QUICK START:

1. INSTALL PYTHON (if not already installed):
   - Windows: Download from https://python.org (check "Add Python to PATH")
   - Mac: Download from https://python.org or use: brew install python
   - Linux: Use package manager (apt, yum, pacman)

2. RUN THE APPLICATION:
   - Windows: Double-click "run_windows.bat"
   - Mac: Double-click "run_mac.sh" or run: ./run_mac.sh
   - Linux: Run: ./run_linux.sh

3. USE THE APPLICATION:
   - Browser will open automatically at http://localhost:8501
   - If browser doesn't open, manually go to http://localhost:8501
   - Add your customers and start managing deliveries!

📁 FILES INCLUDED:
- app.py                    # Main web application
- requirements_web.txt      # Python dependencies
- run_windows.bat          # Windows start script
- run_mac.sh               # Mac start script
- run_linux.sh             # Linux start script
- customers.xlsx           # Your customer data (auto-created)
- README_WEB_APP.txt       # This file

🔧 TROUBLESHOOTING:

If you get "Python not found" error:
- Make sure Python is installed
- On Windows: Check "Add Python to PATH" during installation
- Restart your computer after installing Python

If you get "Package installation failed" error:
- Check your internet connection
- Try running the script again
- On Windows: Run Command Prompt as Administrator

If the browser doesn't open automatically:
- Manually go to http://localhost:8501
- Make sure no other application is using port 8501

If you get "Permission denied" on Mac/Linux:
- Run: chmod +x run_mac.sh run_linux.sh
- Or run: python3 -m streamlit run app.py

If the session ends quickly or you get errors:
1. Run the test script first: python test_app.py
2. Try the debug version: debug_run.bat (Windows)
3. Check if all packages are installed correctly
4. Make sure no antivirus is blocking the application

If you get "Session ended very soon after starting":
- This usually means there's an import error
- Run: python test_app.py to check for issues
- Try: debug_run.bat for detailed error messages

📞 SUPPORT:
If you have any issues, contact your developer with:
- Your operating system (Windows/Mac/Linux)
- Any error messages you see
- Screenshots if possible

🎉 ENJOY YOUR DELIVERY MANAGER!
