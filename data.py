from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    signed = db.Column(db.String(80), unique=True, nullable=False)
    signed_date = db.Column(db.DateTime, default=datetime.utcnow)
    participant_code = db.Column(db.String(80), unique=True, nullable=False) #shown to the user so they can request their data is removed

    data_deletion_requested = db.Column(db.Boolean, default=False)
    data_deletion_date = db.Column(db.DateTime, nullable=True)
    data_deleted = db.Column(db.Boolean, default=False)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    game_dev_experience = db.Column(db.String(1000))
    programming_experience = db.Column(db.String(1000))
    languages = db.Column(db.Text)  # JSON string of selected languages
    uses_ai_tools = db.Column(db.Boolean)
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