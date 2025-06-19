#!/usr/bin/env python3
"""
AI Monitor Setup Script
Helps users get started quickly with the AI monitoring system
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('env_example.txt'):
            shutil.copy('env_example.txt', '.env')
            print("✅ Created .env file from example")
            print("📝 Please edit .env file with your preferred settings")
        else:
            print("❌ env_example.txt not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def test_system():
    """Test the monitoring system"""
    print("🧪 Testing the monitoring system...")
    try:
        # Import and test basic functionality
        from database import AIMonitoringDB
        db = AIMonitoringDB()
        print("✅ Database connection successful")
        
        from notifications import NotificationManager
        nm = NotificationManager()
        print("✅ Notification system initialized")
        
        return True
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 AI Updates Monitor Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Test system
    if not test_system():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your email settings (optional)")
    print("2. Run: py main.py --test-notification")
    print("3. Run: py main.py --run-once")
    print("4. Start monitoring: py main.py")
    
    return True

if __name__ == "__main__":
    main() 