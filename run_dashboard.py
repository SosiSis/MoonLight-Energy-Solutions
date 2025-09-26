#!/usr/bin/env python3
"""
Run script for the MoonLight Energy Solutions Solar Analysis Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Change to project directory
    os.chdir(project_root)

    # Launch Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "app/main.py",
        "--server.headless", "true",
        "--server.address", "localhost",
        "--server.port", "8501"
    ]

    print("🚀 Starting MoonLight Energy Solutions Solar Analysis Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("❌ Press Ctrl+C to stop the server")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()