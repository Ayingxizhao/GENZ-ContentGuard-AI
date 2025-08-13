#!/usr/bin/env python3
"""
ContentGuard AI - Application Launcher
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import pandas
        import openai
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please install required packages:")
        print("  pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✓ Environment file (.env) found")
        return True
    else:
        print("✗ Environment file (.env) not found")
        print("Please create a .env file with your OpenAI API key:")
        print("  OPENAI_API_KEY=your_api_key_here")
        return False

def start_application():
    """Start the Flask application"""
    print("\nStarting ContentGuard AI...")
    print("=" * 40)
    
    try:
        # Import and validate config
        from config import Config
        Config.validate_config()
        print("✓ Configuration validated")
        
        # Import and start app
        from app import app
        print("✓ Application loaded successfully")
        print("\n🚀 ContentGuard AI is starting...")
        print("📱 Open your browser to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the application")
        print("=" * 40)
        
        # Start the app
        app.run(debug=Config.DEBUG, host='0.0.0.0', port=5001)
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("Please check your .env file and API key")
        return False
    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        return False

def main():
    """Main launcher function"""
    print("ContentGuard AI - Malicious Content Detection")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Start application
    if not start_application():
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
        print("Thank you for using ContentGuard AI!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Please check the error message above and try again")
        sys.exit(1)
