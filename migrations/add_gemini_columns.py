#!/usr/bin/env python3
"""
Database migration: Add Gemini tracking columns to users table

This script adds the following columns to the users table:
- gemini_calls_count: Total Gemini API calls (lifetime)
- gemini_calls_today: Gemini API calls today
- last_gemini_call: Timestamp of last Gemini call
- gemini_daily_limit: Daily limit for Gemini calls (default: 10)

Usage:
    python migrations/add_gemini_columns.py

Requirements:
    - DATABASE_URL environment variable must be set
    - PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    query = text("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND column_name = :column_name
        );
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"table_name": table_name, "column_name": column_name})
        return result.scalar()


def add_gemini_columns(engine):
    """Add Gemini tracking columns to users table"""
    
    columns_to_add = [
        {
            "name": "gemini_calls_count",
            "sql": "ALTER TABLE users ADD COLUMN gemini_calls_count INTEGER NOT NULL DEFAULT 0;"
        },
        {
            "name": "gemini_calls_today",
            "sql": "ALTER TABLE users ADD COLUMN gemini_calls_today INTEGER NOT NULL DEFAULT 0;"
        },
        {
            "name": "last_gemini_call",
            "sql": "ALTER TABLE users ADD COLUMN last_gemini_call TIMESTAMP;"
        },
        {
            "name": "gemini_daily_limit",
            "sql": "ALTER TABLE users ADD COLUMN gemini_daily_limit INTEGER NOT NULL DEFAULT 10;"
        }
    ]
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            for column in columns_to_add:
                column_name = column["name"]
                
                # Check if column already exists
                if check_column_exists(engine, "users", column_name):
                    print(f"✓ Column '{column_name}' already exists, skipping...")
                    continue
                
                # Add the column
                print(f"Adding column '{column_name}'...")
                conn.execute(text(column["sql"]))
                print(f"✓ Column '{column_name}' added successfully")
            
            # Commit transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise


def main():
    """Main migration function"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file or environment")
        sys.exit(1)
    
    # Handle Heroku/DigitalOcean postgres:// vs postgresql:// URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 60)
    print("Database Migration: Add Gemini Columns")
    print("=" * 60)
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
        
        print()
        
        # Run migration
        add_gemini_columns(engine)
        
        print()
        print("=" * 60)
        print("Migration Summary:")
        print("- gemini_calls_count: Tracks total Gemini API calls")
        print("- gemini_calls_today: Tracks daily Gemini API calls")
        print("- last_gemini_call: Timestamp of last call")
        print("- gemini_daily_limit: Daily limit (default: 10)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed with error:")
        print(f"   {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
