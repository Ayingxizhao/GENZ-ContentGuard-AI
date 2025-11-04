#!/usr/bin/env python3
"""
Admin Creation Script for ContentGuard AI

Development-only script to create admin accounts for testing.
This script only works in development environment with proper environment variables.
"""

import os
import sys

def check_development_environment():
    """Check if we're in a safe development environment"""
    required_vars = {
        'FLASK_ENV': 'development',
        'ENABLE_ADMIN_ROUTES': 'true'
    }
    
    for var, expected in required_vars.items():
        actual = os.getenv(var, '').lower()
        if actual != expected:
            print(f"❌ Security check failed: {var} should be '{expected}' but is '{actual}'")
            print("   Admin creation is only allowed in development environment")
            return False
    
    return True

def create_admin_user():
    """Create an admin user for testing"""
    if not check_development_environment():
        print("\n🔒 Security measures are working correctly!")
        print("   Admin creation is disabled in production/unknown environments")
        return False
    
    try:
        # Import only after security checks pass
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from models import db, User
        from app import app
        
        print("✅ Development environment confirmed")
        print("🔧 Creating admin user...")
        
        with app.app_context():
            # Default admin credentials
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@test.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin_name = os.getenv('ADMIN_NAME', 'Test Admin')
            
            # Check if admin already exists
            existing_admin = User.query.filter_by(email=admin_email).first()
            if existing_admin:
                if existing_admin.is_admin:
                    print(f"✅ Admin user {admin_email} already exists")
                    print(f"   Password: {admin_password}")
                    return True
                else:
                    print(f"📝 Promoting existing user {admin_email} to admin")
                    existing_admin.make_admin()
                    print(f"✅ User {admin_email} promoted to admin")
                    return True
            
            # Create new admin user
            admin_user = User.create_admin_user(admin_email, admin_password, admin_name)
            
            print(f"✅ Admin user created successfully!")
            print(f"   📧 Email: {admin_email}")
            print(f"   🔑 Password: {admin_password}")
            print(f"   👤 Name: {admin_name}")
            print(f"   🎯 Admin ID: {admin_user.id}")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage():
    """Show usage information"""
    print("Admin Creation Script for ContentGuard AI")
    print("=" * 50)
    print("\n🔒 This script only works in development environment")
    print("   Required environment variables:")
    print("   - FLASK_ENV=development")
    print("   - ENABLE_ADMIN_ROUTES=true")
    print("\n📝 Optional environment variables:")
    print("   - ADMIN_EMAIL (default: admin@test.com)")
    print("   - ADMIN_PASSWORD (default: admin123)")
    print("   - ADMIN_NAME (default: Test Admin)")
    print("\n💡 Usage:")
    print("   python admin/create_admin.py")
    print("\n🌐 After creation, you can:")
    print("   - Login at: http://localhost:5000/auth/login")
    print("   - Test admin features at: http://localhost:5000/admin/test")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['help', '--help', '-h']:
        show_usage()
        return
    
    print("🚀 Starting admin creation process...")
    
    if create_admin_user():
        print("\n🎉 Admin setup completed!")
        print("   You can now start the application and test admin features.")
        print("   Run: conda activate contentguard && python run.py")
    else:
        print("\n❌ Admin creation failed or was blocked by security measures.")
        print("   This is normal in production environments.")

if __name__ == "__main__":
    main()
