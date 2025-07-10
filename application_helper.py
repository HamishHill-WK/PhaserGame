import os
import random
import json

def is_development_mode():
    return os.environ.get('FLASK_ENV', '').lower() == 'development'

def assign_balanced_condition(User, expertise_level=None):
    try:
        ai_count = 0
        control_count = 0
        if expertise_level == 'low':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='low').count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='low').count() or 0
        elif expertise_level == 'medium':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='medium').count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='medium').count() or 0
        elif expertise_level == 'high':
            ai_count = User.query.filter_by(assigned_condition='ai', expertise_level='high').count() or 0
            control_count = User.query.filter_by(assigned_condition='control', expertise_level='high').count() or 0
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
    user_id = session.get('user_id')
    if user_id is None:
        return None
    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None

def categorize_expertise_from_existing_survey(survey_data):
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
    course_related = getattr(survey_data, 'course_related', False) 
    
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
    
    if prog_professional or game_professional:
        if prog_professional in ['lead'] or game_professional in ['lead']:
            expertise_indicators += 3
        elif prog_professional in ['senior'] or game_professional in ['senior']:
            expertise_indicators += 2.5
        elif prog_professional in ['mid'] or game_professional in ['mid']:
            expertise_indicators += 2
        elif prog_professional in ['junior'] or game_professional in ['junior']:
            expertise_indicators += 1.5
    else:
        if prog_level == 'professional' or game_level == 'professional':
            expertise_indicators += 2
        elif prog_level == 'advanced' or game_level == 'advanced':
            expertise_indicators += 1.5
        elif prog_level == 'moderate' or game_level == 'moderate':
            expertise_indicators += 1
        
    if 'javascript' in languages:
        expertise_indicators += 2 
    if used_phaser:
        expertise_indicators += 2 
    if len(languages) >= 5:
        expertise_indicators += 1.5  # Strong breadth
    elif len(languages) >= 3:
        expertise_indicators += 1  # Good breadth
        
    if course_prog_exp:
        course_score = 0
        if 'large_projects' in course_prog_exp:
            course_score = 1.5
        elif 'advanced_modules' in course_prog_exp:
            course_score = 1
        elif 'intro_modules' in course_prog_exp:
            course_score = 0.5
        
        if course_related:
            expertise_indicators += course_score
        else:
            expertise_indicators += course_score * 0.75
    
    if 'released_app' in self_taught_exp:
        expertise_indicators += 2  
    elif 'spare_time_projects' in self_taught_exp:
        expertise_indicators += 1.5
    elif 'intro_tutorials' in self_taught_exp:
        expertise_indicators += 0.5
    
    max_years = max(prog_years, game_years)
    if max_years >= 10:
        expertise_indicators += 1.5
    elif max_years >= 5:
        expertise_indicators += 1
    elif max_years >= 2:
        expertise_indicators += 0.5
    
    if len(engines) >= 3:
        expertise_indicators += 1
    elif len(engines) >= 1 and 'none' not in engines:
        expertise_indicators += 0.5
        
    if expertise_indicators >= 10:
        return 'high'
    elif expertise_indicators >= 6:
        return 'medium'
    else:
        return 'low'
    
