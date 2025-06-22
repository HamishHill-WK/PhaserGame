#!/usr/bin/env python3
"""
Database Setup Script for Phaser Research Application
Run this script to initialize your PostgreSQL database on AWS RDS
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Initialize the database with all required tables"""
    try:
        # Import after adding to path
        from app import app, db
        from data import User, Survey, ExperimentData, CodeChange
        
        print("🚀 Starting database setup...")
        print(f"📊 Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        
        with app.app_context():
            # Drop all tables (use with caution!)
            # db.drop_all()
            # print("🗑️  Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("✅ Created all database tables successfully!")
            
            # Verify tables were created
            tables = db.engine.table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        from app import app, db
        
        with app.app_context():
            # Test connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure your DATABASE_URL is correct in .env file")
        return False

if __name__ == "__main__":
    print("🔧 Phaser Research Database Setup")
    print("=" * 40)
    
    # Check if environment is configured
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not found in environment")
        print("💡 Please copy .env.template to .env and configure your database settings")
        sys.exit(1)
    
    # Test connection first
    if test_connection():
        # Setup database
        if setup_database():
            print("\n🎉 Database setup completed successfully!")
            print("🚀 You can now run your Flask application")
        else:
            print("\n❌ Database setup failed")
            sys.exit(1)
    else:
        print("\n❌ Cannot connect to database")
        sys.exit(1)
