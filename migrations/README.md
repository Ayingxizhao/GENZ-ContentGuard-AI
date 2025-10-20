# Database Migrations

This directory contains database migration scripts for schema changes.

## Available Migrations

### add_gemini_columns.py
**Date**: Oct 20, 2025  
**Purpose**: Add Gemini API tracking columns to users table

**Adds columns:**
- `gemini_calls_count` - Total lifetime Gemini API calls
- `gemini_calls_today` - Gemini API calls today
- `last_gemini_call` - Timestamp of last Gemini call
- `gemini_daily_limit` - Daily limit for Gemini calls (default: 10)

**Usage:**
```bash
python migrations/add_gemini_columns.py
```

**Requirements:**
- `DATABASE_URL` environment variable must be set
- PostgreSQL database
- SQLAlchemy installed

## Running Migrations

### Local Development
```bash
# Make sure DATABASE_URL is set in .env
python migrations/add_gemini_columns.py
```

### Production (DigitalOcean)
```bash
# Option 1: SSH into your app and run
python migrations/add_gemini_columns.py

# Option 2: Run locally against production DB
export DATABASE_URL="your-production-database-url"
python migrations/add_gemini_columns.py
```

## Safety Features

All migration scripts are designed to be:
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Transactional**: Changes are rolled back on error
- ✅ **Verified**: Check if changes already exist before applying

## Troubleshooting

**Error: DATABASE_URL not set**
```bash
# Set in .env file or export directly
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
```

**Error: Connection refused**
- Check if database is running
- Verify DATABASE_URL is correct
- Check firewall/network settings

**Error: Permission denied**
- Ensure database user has ALTER TABLE permissions
- Contact database administrator if needed
