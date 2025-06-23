#!/usr/bin/env python3
"""
Database Setup Script for Phaser Research Application
Run this script to initialize your PostgreSQL database on AWS RDS
"""
from app import app, db
from data import User, Survey, ExperimentData, CodeChange
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
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Verify tables were created
            tables = db.engine.table_names()
            
            return True
            
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:        
        with app.app_context():
            # Test connection
            db.engine.execute('SELECT 1')
            return True
            
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Check if environment is configured
    if not os.getenv('DATABASE_URL'):
        sys.exit(1)
    
    # Test connection first
    if test_connection():
        # Setup database
        if setup_database():
            print("\nDatabase setup completed successfully!")
        else:
            print("\nDatabase setup failed")
            sys.exit(1)
    else:
        print("\nCannot connect to database")
        sys.exit(1)
