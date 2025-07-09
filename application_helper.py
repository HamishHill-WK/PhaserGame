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
    
    # Relevant experience fields
    used_phaser = getattr(survey_data, 'used_phaser', False)
    course_related = getattr(survey_data, 'course_related', False)  # NEW FIELD
    
    try:
        self_taught_exp = json.loads(getattr(survey_data, 'self_taught_experience', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        self_taught_exp = []
    
    try:
        course_prog_exp = json.loads(getattr(survey_data, 'course_programming_experience', '[]') or '[]')
    except (json.JSONDecodeError, TypeError):
        course_prog_exp = []
    
    # Research-based scoring
    expertise_indicators = 0
    
    # 1. Professional context (avoid double-scoring)
    if prog_professional or game_professional:
        # Score based on professional position
        if prog_professional in ['lead'] or game_professional in ['lead']:
            expertise_indicators += 3
        elif prog_professional in ['senior'] or game_professional in ['senior']:
            expertise_indicators += 2.5
        elif prog_professional in ['mid'] or game_professional in ['mid']:
            expertise_indicators += 2
        elif prog_professional in ['junior'] or game_professional in ['junior']:
            expertise_indicators += 1.5
    else:
        # Score based on experience level if no professional position
        if prog_level == 'professional' or game_level == 'professional':
            expertise_indicators += 2
        elif prog_level == 'advanced' or game_level == 'advanced':
            expertise_indicators += 1.5
        elif prog_level == 'moderate' or game_level == 'moderate':
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
        
    # 3. Course programming experience (now weighted by relevance)
    if course_prog_exp:  # Only score if they have course experience
        # Calculate base course score
        course_score = 0
        if 'large_projects' in course_prog_exp:
            course_score = 1.5
        elif 'advanced_modules' in course_prog_exp:
            course_score = 1
        elif 'intro_modules' in course_prog_exp:
            course_score = 0.5
        
        # Apply relevance multiplier
        if course_related:
            expertise_indicators += course_score
        else:
            expertise_indicators += course_score * 0.75
    
    # 4. Self-taught experience (shows initiative and practical skills)
    if 'released_app' in self_taught_exp:
        expertise_indicators += 2  # Very strong indicator
    elif 'spare_time_projects' in self_taught_exp:
        expertise_indicators += 1.5
    elif 'intro_tutorials' in self_taught_exp:
        expertise_indicators += 0.5
    
    # 5. Experience years (research: weak predictor, so minimal weight)
    max_years = max(prog_years, game_years)
    if max_years >= 10:
        expertise_indicators += 1.5
    elif max_years >= 5:
        expertise_indicators += 1
    elif max_years >= 2:
        expertise_indicators += 0.5
    
    # 6. Game engine experience
    if len(engines) >= 3:
        expertise_indicators += 1
    elif len(engines) >= 1 and 'none' not in engines:
        expertise_indicators += 0.5
    
    # Research-informed categorization
    
    # Research-informed categorization
    if expertise_indicators >= 10:
        return 'high'
    elif expertise_indicators >= 6:
        return 'medium'
    else:
        return 'low'
    
