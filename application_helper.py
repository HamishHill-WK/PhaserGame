import os
import random
from datetime import datetime
from dateutil.parser import isoparse
import json

def is_development_mode():
    """Return True if FLASK_ENV is set to 'development'."""
    return os.environ.get('FLASK_ENV', '').lower() == 'development'

def assign_balanced_condition(User, expertise_level=None):
    """
    Assign participant to AI or Control condition based on current balance.
    Args:
        User: SQLAlchemy User model class
    Returns: 'ai' or 'control'
    """
    try:
        ai_count = 0
        control_count = 0
        if expertise_level is 'low':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='low', consent_participate=True).count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='low', consent_participate=True).count() or 0
        elif expertise_level is 'medium':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='medium', consent_participate=True).count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='medium', consent_participate=True).count() or 0
        elif expertise_level is 'high':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='high', consent_participate=True).count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='high', consent_participate=True).count() or 0
        
        total_count = ai_count + control_count
        print(f"Current balance - AI: {ai_count}, Control: {control_count}")
        if total_count == 0:
            assigned_condition = 'ai'
        elif ai_count < control_count:
            assigned_condition = 'ai'
        elif control_count < ai_count:
            assigned_condition = 'control'
        else:
            assigned_condition = 'ai'
        print(f"Assigned condition: {assigned_condition}")
        
        return assigned_condition
    except Exception as e:
        print(f"Error in condition assignment: {e}")
        return random.choice(['ai', 'control'])

def get_int_user_id(session):
    """
    Get integer user_id from session.
    Args:
        session: Flask session object
    Returns: int user_id or None
    """
    user_id = session.get('user_id')
    if user_id is None:
        return None
    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None

def categorize_expertise_from_existing_survey(survey_data):
    """
    Categorize expertise level based on survey data using research-informed scoring.
    
    Args:
        survey_data: Survey object with all survey responses
    
    Returns:
        str: 'low', 'medium', or 'high' expertise level
    """
    
    # Extract fields (using attribute access for SQLAlchemy objects)
    prog_level = getattr(survey_data, 'programming_experience_level', 'none') or 'none'
    game_level = getattr(survey_data, 'game_dev_experience_level', 'none') or 'none'
    prog_years = getattr(survey_data, 'programming_experience_years', 0) or 0
    game_years = getattr(survey_data, 'game_dev_experience_years', 0) or 0
    
    # Handle JSON fields
    try:
        languages = json.loads(getattr(survey_data, 'programming_languages', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        languages = []
    
    try:
        engines = json.loads(getattr(survey_data, 'game_engines', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        engines = []
    
    # Professional levels
    prog_professional = getattr(survey_data, 'programming_proffessional_level', None)
    game_professional = getattr(survey_data, 'game_dev_proffessional_level', None)
    
    # New fields
    used_phaser = getattr(survey_data, 'used_phaser', False)
    is_student = getattr(survey_data, 'is_student', False)
    is_graduate = getattr(survey_data, 'is_graduate', False)
    is_self_taught = getattr(survey_data, 'is_self_taught', False)
    
    # Educational experience fields
    try:
        self_taught_exp = json.loads(getattr(survey_data, 'self_taught_experience', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        self_taught_exp = []
    
    try:
        course_prog_exp = json.loads(getattr(survey_data, 'course_programming_experience', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        course_prog_exp = []
    
    degree_current = getattr(survey_data, 'degree_level_current', None)
    degree_highest = getattr(survey_data, 'degree_level_highest', None)
    undergrad_year = getattr(survey_data, 'undergrad_year', None)
    
    # Research-based scoring using existing and new data
    expertise_indicators = 0
    
    # 1. Professional context (research: strongest indicator after aptitude)
    if prog_professional == 'professional' or game_professional == 'professional':
        expertise_indicators += 3
    elif prog_level == 'professional' or game_level == 'professional':
        expertise_indicators += 2
    elif prog_professional in ['senior', 'lead'] or game_professional in ['senior', 'lead']:
        expertise_indicators += 2
    elif prog_professional in ['mid'] or game_professional in ['mid']:
        expertise_indicators += 1
        
    # 2. Tool-specific knowledge (research: better predictor than general experience)
    if 'javascript' in languages:
        expertise_indicators += 2  # Directly relevant to your study
    if used_phaser:
        expertise_indicators += 2  # Highly relevant to Phaser.js study
    if len(languages) >= 5:
        expertise_indicators += 1.5  # Strong breadth
    elif len(languages) >= 3:
        expertise_indicators += 1  # Good breadth
        
    # 3. Domain expertise
    if game_level in ['advanced', 'professional']:
        expertise_indicators += 2
    elif game_level == 'moderate':
        expertise_indicators += 1
        
    # 4. Programming competence
    if prog_level in ['advanced', 'professional']:
        expertise_indicators += 2
    elif prog_level == 'moderate':
        expertise_indicators += 1
        
    # 5. Educational background (new scoring)
    # Graduate degree holders
    if degree_highest == 'phd':
        expertise_indicators += 2
    elif degree_highest == 'masters':
        expertise_indicators += 1.5
    elif degree_highest == 'undergraduate':
        expertise_indicators += 1
    
    # Current students
    if is_student:
        if degree_current == 'phd':
            expertise_indicators += 1.5
        elif degree_current == 'masters':
            expertise_indicators += 1
        elif degree_current == 'undergraduate':
            # Consider year level
            if undergrad_year in ['3', '4']:
                expertise_indicators += 0.5
    
    # Course programming experience
    if 'large_projects' in course_prog_exp:
        expertise_indicators += 1.5
    elif 'advanced_modules' in course_prog_exp:
        expertise_indicators += 1
    elif 'intro_modules' in course_prog_exp:
        expertise_indicators += 0.5
    
    # Self-taught experience (shows initiative and practical skills)
    if 'released_app' in self_taught_exp:
        expertise_indicators += 2  # Very strong indicator
    elif 'spare_time_projects' in self_taught_exp:
        expertise_indicators += 1.5
    elif 'intro_tutorials' in self_taught_exp:
        expertise_indicators += 0.5
    
    # 6. Experience years (research: weak predictor, so minimal weight)
    max_years = max(prog_years, game_years)
    if max_years >= 10:
        expertise_indicators += 1.5
    elif max_years >= 5:
        expertise_indicators += 1
    elif max_years >= 2:
        expertise_indicators += 0.5
    
    # 7. Game engine experience
    if len(engines) >= 3:
        expertise_indicators += 1
    elif len(engines) >= 1 and 'none' not in engines:
        expertise_indicators += 0.5
    
    if expertise_indicators >= 8:
        return 'high'
    elif expertise_indicators >= 4:
        return 'medium'
    else:
        return 'low'