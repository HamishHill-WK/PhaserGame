from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

# Create database instance
db = SQLAlchemy()

def configure_database(application):
    """Configure database settings and initialize with Flask application"""
    
    # Database configuration - PostgreSQL for AWS RDS
    DATABASE_URL = os.environ.get('EXPERIMENT_DATA_LINK') 
    
        # Get DATABASE_URL and map it to SQLALCHEMY_DATABASE_URI
    if DATABASE_URL:
        application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'pool_recycle': 120,
            'pool_pre_ping': True,
            'connect_args': {
                'sslmode': 'require'  # AWS RDS requires SSL
            }
        }
        
    print(application.config)

    # Initialize database with application
    db.init_app(application)
    
    return db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    signed = db.Column(db.String(80), unique=True, nullable=False)
    signed_date = db.Column(db.DateTime, default=datetime.utcnow)
    consent_data = db.Column(db.Boolean, nullable=False)  
    consent_participate = db.Column(db.Boolean, default=False)  # User consent to participate in the study
    participant_code = db.Column(db.String(80), unique=True, nullable=False) #shown to the user so they can request their data is removed

    data_deletion_requested = db.Column(db.Boolean, default=False)
    data_deletion_date = db.Column(db.DateTime, nullable=True)
    data_deleted = db.Column(db.Boolean, default=False)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # Link to user session
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    game_dev_experience_description = db.Column(db.String(1000))
    game_dev_experience_level = db.Column(db.String(100))  # e.g., Beginner, Intermediate, Advanced
    game_dev_proffessional_level = db.Column(db.String(100))  # e.g., Hobbyist, Professional
    game_dev_experience_years = db.Column(db.Float, nullable=True)
    game_engines = db.Column(db.Text)  # JSON string of selected game engines
    
    programming_experience_description = db.Column(db.String(1000))
    programming_experience_years = db.Column(db.Float, nullable=True)
    programming_experience_level = db.Column(db.String(100))  # e.g., Beginner, Intermediate, Advanced
    programming_proffessional_level = db.Column(db.String(100))  # e.g., Hobbyist, Professional
    programming_languages = db.Column(db.Text)  # JSON string of selected languages
    used_phaser = db.Column(db.Boolean, default=False)
    phaser_experience_description = db.Column(db.String(1000))
    
    uses_ai_tools = db.Column(db.Boolean)
    ai_tools_description = db.Column(db.String(1000))
    ai_usage_details = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExperimentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    with_ai = db.Column(db.Boolean, default=False)
    user_action = db.Column(db.String(1000))
    error_count = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)  # JSON string of error messages
    conversation = db.Column(db.Text)  # JSON string of prompts
    code = db.Column(db.Text)  # JSON string of code snippets
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text)  # JSON string for additional data
    
    def log_error(self, error_message, ):
        if self.error_messages:
            self.error_messages = f"{self.error_messages}\n{error_message}timestamp: {datetime.now()}"
        else:
            self.error_messages = error_message
        self.error_count += 1
        
class CodeChange(db.Model):
    edit_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    experiment_data_id = db.Column(db.Integer, db.ForeignKey('experiment_data.id'), nullable=False)
    
    code_before = db.Column(db.Text, nullable=False)
    code_after = db.Column(db.Text, nullable=False)
    
    lines_changed = db.Column(db.Integer, nullable=False)
    lines_added = db.Column(db.Integer, nullable=False)
    lines_removed = db.Column(db.Integer, nullable=False)
    
    errors_before = db.Column(db.Integer, nullable=False)
    errors_after = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)