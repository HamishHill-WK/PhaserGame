from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import json

# Create database instance
db = SQLAlchemy()

def is_development_mode():
    """Return True if FLASK_ENV is set to 'development'."""
    return os.environ.get('FLASK_ENV', '').lower() == 'development'

def configure_database(application):
    """Configure database settings and initialize with Flask application"""
    #DATABASE_URL = os.environ.get('DATABASE_URL')
    #if not DATABASE_URL:
    rds_hostname = os.environ.get('RDS_HOSTNAME')
    rds_port = os.environ.get('RDS_PORT', '5432')
    rds_db_name = os.environ.get('RDS_DB_NAME')
    rds_username = os.environ.get('RDS_USERNAME')
    rds_password = os.environ.get('RDS_PASSWORD')
    if all([rds_hostname, rds_db_name, rds_username, rds_password]):
        DATABASE_URL = f"postgresql://{rds_username}:{rds_password}@{rds_hostname}:{rds_port}/{rds_db_name}"
    if DATABASE_URL:
        application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if is_development_mode():
            application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 5,
                'pool_recycle': 60,
                'pool_pre_ping': True,
                'connect_args': {
                    'sslmode': 'prefer'
                }
            }
        else:
            application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 10,
                'pool_recycle': 120,
                'pool_pre_ping': True,
                'connect_args': {
                    'sslmode': 'require'  # AWS RDS requires SSL
                }
            }
    else:
        raise ValueError("No database configuration found. Please set DATABASE_URL or RDS environment variables.")
    #'print(f"Final DATABASE_URL: {DATABASE_URL}")
   # print(application.config)
    db.init_app(application)
    return db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_code = db.Column(db.String(80), unique=True, nullable=False) #shown to the user so they can request their data is removed
    assigned_condition = db.Column(db.String(20), nullable=True)  # 'ai' or 'control'
    expertise_level = db.Column(db.String(100), nullable=True)  # e.g., Beginner, Intermediate, Advanced
    signed_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date when user signed up

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # Link to user session
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    participant_code = db.Column(db.String(80), nullable=False)  # Unique code for user
    
    game_dev_experience_level = db.Column(db.String(100))  # e.g., Beginner, Intermediate, Advanced
    game_dev_proffessional_level = db.Column(db.String(100))  # e.g., Hobbyist, Professional
    game_dev_experience_years = db.Column(db.Float, nullable=True)
    game_engines = db.Column(db.Text)  # JSON string of selected game engines
    
    programming_experience_years = db.Column(db.Float, nullable=True)
    programming_experience_level = db.Column(db.String(100))  # e.g., Beginner, Intermediate, Advanced
    programming_proffessional_level = db.Column(db.String(100))  # e.g., Hobbyist, Professional
    programming_languages = db.Column(db.Text)  # JSON string of selected languages
    used_phaser = db.Column(db.Boolean, default=False)
    
    uses_ai_tools = db.Column(db.Boolean)
    ai_tools_description = db.Column(db.String(1000))
    ai_usage_details = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    is_student = db.Column(db.Boolean, default=False)
    is_graduate = db.Column(db.Boolean, default=False)
    is_self_taught = db.Column(db.Boolean, default=False)
    self_taught_experience = db.Column(db.Text)  # JSON string of selected self-taught experiences
    degree_level_current = db.Column(db.String(50))
    degree_level_highest = db.Column(db.String(50))
    course_programming_experience = db.Column(db.Text)  # JSON string of selected course programming experiences
    undergrad_year = db.Column(db.String(10))
    course_related = db.Column(db.Boolean, default=False)  # Whether the course is related to CS or Game Dev
    
    description = db.Column(db.String(1000))

class ExperimentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participant_code = db.Column(db.String(80), nullable=False)  # Unique code for user
    session_id = db.Column(db.String(100), nullable=False)
    with_ai = db.Column(db.Boolean, default=False)
    user_action = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text)  # JSON string for additional data

class CodeChange(db.Model):
    edit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participant_code = db.Column(db.String(80), nullable=False)  # Unique code for user
    
    code_before = db.Column(db.Text, nullable=False)
    code_after = db.Column(db.Text, nullable=False)
    
    lines_changed = db.Column(db.Integer, nullable=False)
    lines_added = db.Column(db.Integer, nullable=False)
    lines_removed = db.Column(db.Integer, nullable=False)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class TaskCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participant_code = db.Column(db.String(80), nullable=False)  # Unique code for user
    session_id = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.String(50), nullable=False)  # e.g., 'task1', 'task2', etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class SUS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    participant_code = db.Column(db.String(80), nullable=False)
    
    q1_use_frequently = db.Column(db.Integer, nullable=False)
    q2_unnecessarily_complex = db.Column(db.Integer, nullable=False)
    q3_easy_to_use = db.Column(db.Integer, nullable=False)
    q4_need_technical_support = db.Column(db.Integer, nullable=False)
    q5_functions_integrated = db.Column(db.Integer, nullable=False)
    q6_too_much_inconsistency = db.Column(db.Integer, nullable=False)
    q7_learn_quickly = db.Column(db.Integer, nullable=False)
    q8_cumbersome_to_use = db.Column(db.Integer, nullable=False)
    q9_felt_confident = db.Column(db.Integer, nullable=False)
    q10_learn_lot_before_use = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)