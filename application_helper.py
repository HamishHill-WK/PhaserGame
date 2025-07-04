import os
import random
from datetime import datetime
from dateutil.parser import isoparse

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
        if expertise_level is 'low':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='low', consent_participate=True).count()
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='low', consent_participate=True).count()
        elif expertise_level is 'medium':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='medium', consent_participate=True).count()
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='medium', consent_participate=True).count()
        elif expertise_level is 'high':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='high', consent_participate=True).count()
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='high', consent_participate=True).count()
        
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
    
    # Extract your existing fields
    prog_level = survey_data.get('programming_experience_level', 'none')
    game_level = survey_data.get('game_dev_experience_level', 'none') 
    prog_years = survey_data.get('programming_experience_years', 0) or 0
    game_years = survey_data.get('game_dev_experience_years', 0) or 0
    languages = survey_data.get('programming_languages', [])
    engines = survey_data.get('game_engines', [])
    used_phaser = survey_data.get('used_phaser', False)
    prog_professional = survey_data.get('programming_proffessional_level')
    game_professional = survey_data.get('game_dev_proffessional_level')
    
    # Research-based scoring using existing data
    expertise_indicators = 0
    
    # 1. Professional context (research: strongest indicator after aptitude)
    if prog_professional == 'professional' or game_professional == 'professional':
        expertise_indicators += 3
    elif prog_level == 'professional' or game_level == 'professional':
        expertise_indicators += 2
        
    # 2. Tool-specific knowledge (research: better predictor than general experience)
    if 'javascript' in languages:
        expertise_indicators += 2  # Directly relevant to your study
    if used_phaser:
        expertise_indicators += 2  # Highly relevant
    if len(languages) >= 3:
        expertise_indicators += 1  # Breadth indicator
        
    # 3. Domain expertise (research: context-dependent)
    if game_level in ['advanced', 'professional']:
        expertise_indicators += 2
    elif game_level == 'moderate':
        expertise_indicators += 1
        
    # 4. Programming competence
    if prog_level in ['advanced', 'professional']:
        expertise_indicators += 2
    elif prog_level == 'moderate':
        expertise_indicators += 1
        
    # 5. Experience (research: weak predictor, so minimal weight)
    max_years = max(prog_years, game_years)
    if max_years >= 5:
        expertise_indicators += 1
    elif max_years >= 2:
        expertise_indicators += 0.5
        
    # Research-informed categorization (avoid binary expert/novice)
    if expertise_indicators >= 7:
        return 'high'
    elif expertise_indicators >= 3:
        return 'medium'
    else:
        return 'low'