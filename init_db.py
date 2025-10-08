"""
Database initialization script for production
Run this ONCE after deploying to create tables in PostgreSQL
"""
from app import app, db
from models_analytics import AccessLog  # Import to register analytics models

if __name__ == '__main__':
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {', '.join(tables)}")
        print("  - users: Authentication and usage tracking")
        print("  - access_logs: Analytics and visitor tracking")
