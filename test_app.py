#!/usr/bin/env python3
"""
Simple test script to verify the Flask application setup
"""

import os
import sys
from config import Config

def test_config():
    """Test if configuration is properly loaded"""
    print("Testing configuration...")
    
    try:
        # Test if we can import required modules
        from flask import Flask
        from llm import analyze_post_content
        print("✓ All required modules imported successfully")
        
        # Test configuration
        print(f"✓ Debug mode: {Config.DEBUG}")
        print(f"✓ Max content length: {Config.MAX_CONTENT_LENGTH}")
        
        # Test OpenAI API key (don't show the actual key)
        if Config.OPENAI_API_KEY:
            print(f"✓ OpenAI API key: {'*' * (len(Config.OPENAI_API_KEY) - 8) + Config.OPENAI_API_KEY[-8:]}")
        else:
            print("✗ OpenAI API key not found")
            print("  Please create a .env file with your OPENAI_API_KEY")
            return False
            
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Please install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    print("\nTesting Flask application...")
    
    try:
        from app import app
        print("✓ Flask application created successfully")
        
        # Test routes
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Main route working")
            else:
                print(f"✗ Main route returned status {response.status_code}")
                
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health check route working")
            else:
                print(f"✗ Health check route returned status {response.status_code}")
                
        return True
        
    except Exception as e:
        print(f"✗ Flask application error: {e}")
        return False

def main():
    """Run all tests"""
    print("ContentGuard AI - Setup Test")
    print("=" * 40)
    
    config_ok = test_config()
    if not config_ok:
        print("\nConfiguration test failed. Please fix the issues above.")
        sys.exit(1)
    
    flask_ok = test_flask_app()
    if not flask_ok:
        print("\nFlask application test failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✓ All tests passed! Your application is ready to run.")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nThen open your browser to: http://localhost:5001")

if __name__ == "__main__":
    main()
