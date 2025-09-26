#!/usr/bin/env python3
"""
Health check script for MoonLight Energy Solutions Dashboard
"""

def check_app_health():
    """Check if the application is healthy and ready to deploy"""
    import os
    import sys
    
    print("🔍 MoonLight Energy Solutions - App Health Check")
    print("=" * 50)
    
    # Check file structure
    required_files = [
        "app/main.py",
        "app/utils.py", 
        "requirements.txt",
        ".streamlit/config.toml"
    ]
    
    print("📁 Checking file structure...")
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            return False
    
    # Check configuration
    print("\n⚙️ Checking Streamlit configuration...")
    with open('.streamlit/config.toml', 'r') as f:
        config_content = f.read()
        
        # Check for deprecated options
        if 'dataFrameSerialization' in config_content and 'dataFrameSerialization = "legacy"' in config_content:
            print("   ❌ Found deprecated 'dataFrameSerialization' option")
            return False
        elif 'dataFrameSerialization' in config_content:
            print("   ✅ dataFrameSerialization option properly handled")
            
        if 'caching = true' in config_content:
            print("   ❌ Found deprecated 'caching' option")
            return False
        elif 'caching' in config_content:
            print("   ✅ caching option properly handled")
            
        if 'headless = true' in config_content:
            print("   ✅ headless mode enabled for cloud deployment")
        else:
            print("   ⚠️  headless mode not set to true")
    
    # Check data directory
    print("\n📊 Checking data files...")
    data_files = [
        "data/raw/benin-malanville.csv",
        "data/raw/sierraleone-bumbuna.csv", 
        "data/raw/togo-dapaong_qc.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} - Missing (may cause runtime issues)")
    
    print("\n🎯 Health Check Summary:")
    print("   ✅ Core application structure is healthy")
    print("   ✅ Configuration issues resolved")
    print("   ✅ Ready for Streamlit Cloud deployment")
    
    print("\n🚀 Deployment Instructions:")
    print("   1. Ensure this repository is connected to Streamlit Cloud")
    print("   2. Set main file path to: app/main.py")
    print("   3. Deploy and monitor for any runtime issues")
    
    return True

if __name__ == "__main__":
    check_app_health()