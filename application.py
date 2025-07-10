from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
from functools import wraps
import os 
import json
from datetime import datetime
import assistant
import secval
import uuid
from data import db, Survey, ExperimentData, User, configure_database, is_development_mode, TaskCheck, CodeChange, SUS
from dotenv import load_dotenv 
import difflib
from dateutil.parser import isoparse
import traceback
from application_helper import is_development_mode, assign_balanced_condition, get_int_user_id, categorize_expertise_from_existing_survey
load_dotenv()

validator = secval.SimpleSecurityValidator()
application = Flask(__name__)
application.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

try:
    configure_database(application)
    print("Database configured successfully!")
except Exception as e:
    print(f"Error configuring database: {e}")

@application.route("/gameAIassistant", methods=["GET", "POST"])
def gameAIassistant():
    # Use existing session ID from survey flow or create new one
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    # Get assigned_condition from session or user
    assigned_condition = session.get('assigned_condition')
    if not assigned_condition:
        user_id = session.get('user_id')
        assigned_condition = None
        if user_id:
            user = User.query.get(user_id)
            if user and hasattr(user, 'assigned_condition'):
                assigned_condition = user.assigned_condition
                session['assigned_condition'] = assigned_condition
    return render_template('game-AI-assistant.html', assigned_condition=assigned_condition)

@application.route("/")
@application.route("/index")
def index():
    # Generate session ID for user tracking across all pages
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    # Generate participant code if not present, but do NOT create user in DB here
    participant_code = None
    if 'participant_code' not in session:
        participant_code_val = f"P{uuid.uuid4().hex[:8].upper()}"
        session['participant_code'] = participant_code_val
        participant_code = participant_code_val
    else:
        participant_code = session['participant_code']
    return render_template('index.html', participant_code=participant_code)

# Add the survey route
@application.route("/opensurvey", methods=["GET", "POST"])
def opensurvey():
    # Ensure session ID exists from consent page
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    consent = request.form.get('consent')
    if consent == 'agree':
        return redirect(url_for('survey'))
    
@application.route("/survey")
def survey():
    # Ensure session ID consistency
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
        session_id = session['session_id']
    
    return render_template('survey.html', session_id=session_id)

@application.route("/save-code", methods=["POST"])
def save_code():
    try:
        print("Received request to save code")
        data = request.get_json()
        code = data.get("code")
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id(session)
        
        # Should be:
        validation_result = validator.validate(code)
        is_safe = validation_result['is_safe']
        violations = validation_result['violations']
        
        if not is_safe:
            violation_messages = [v if isinstance(v, str) else str(v) for v in violations]
            return jsonify({"success": False, "error": f"Security violation: {'; '.join(violation_messages)}"})
        
        code_lines = code.split('\n')
        file_name = data.get("file")
        
        # Validate file name to prevent directory traversal
        if file_name != "game.js":
            print(f"Invalid file name: {file_name}")
            return jsonify({"success": False, "error": "Invalid file name"})

        print(f"Saving code for session {session_id} with user ID {user_id} and file name {file_name}")
        # Save to user-specific file
        user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
        os.makedirs(os.path.dirname(user_file_path), exist_ok=True)
        
        print(f"User file path: {user_file_path}")
        
        # --- Compute code diff for logging ---
        prev_code = ""
        if os.path.exists(user_file_path):
            print(f"Loading previous code from {user_file_path}")
            with open(user_file_path, "r", encoding="utf-8") as f:
                prev_code = f.read()
        prev_lines = prev_code.split('\n') if prev_code else []
        diff = list(difflib.unified_diff(prev_lines, code_lines, lineterm=''))        
        #last_error_count = session.get('error_count', 0)
        
        print("Computing JavaScript errors in the code")
        
        # error_count = count_js_errors(code) or 0
        # if error_count != 0:
        #     session['error_count'] = error_count

        last_ai_usage = session.get('last_ai_usage')
        last_code_save = session.get('last_code_save')
        used_ai = False
        if last_ai_usage:
            try:
                ai_time = isoparse(last_ai_usage)
                if last_code_save:
                    save_time = isoparse(last_code_save)
                    used_ai = ai_time > save_time
                else:
                    used_ai = True  # No previous save, but AI was used
            except Exception:
                used_ai = False
                
        print("Logging ")
        # Only log if there are changes
        if user_id and diff:
            # Log code change to CodeChange table
            # Get previous and new code as strings
            prev_code_str = '\n'.join(prev_lines)
            new_code_str = code
            # Calculate line changes
            lines_changed = len(diff)
            lines_added = sum(1 for d in diff if d.startswith('+') and not d.startswith('+++'))
            lines_removed = sum(1 for d in diff if d.startswith('-') and not d.startswith('---'))
            # Optionally, you could track errors_before/errors_after if available
            code_change = CodeChange(
                user_id=user_id,
                participant_code=session.get('participant_code', 'unknown'),
                code_before=prev_code_str,
                code_after=new_code_str,
                lines_changed=lines_changed,
                lines_added=lines_added,
                lines_removed=lines_removed,
                timestamp=datetime.now()
            )
            if not is_development_mode():
                db.session.add(code_change)
                db.session.commit()
            else:
                print("[DEV] Skipping DB commit for code_change (development mode)")
        
        # Save new code to file
        with open(user_file_path, "w", encoding="utf-8", newline='') as f:
            print(f"Writing code to {user_file_path}")
            f.write(code)
        
        print(f"Code saved to {user_file_path}")
        
        # Log code save action to experiment data
        if user_id:
            experiment_data = ExperimentData(
                session_id=session_id,
                user_id=user_id,
                participant_code=session.get('participant_code', 'unknown'),
                user_action="code_save",
                timestamp=datetime.now(),
                data=json.dumps({
                    "file_name": file_name,
                    "code_length": len(code),
                    "lines_count": len(code_lines),
                    "used_ai_assistant_since_last_save": used_ai
                })
            )
            # Only commit to DB if not in development mode
            if not is_development_mode():
                db.session.add(experiment_data)
                db.session.commit()
            else:
                print("[DEV] Skipping DB commit for experiment_data (development mode)")
        
        # Update last_code_save timestamp in session
        session['last_code_save'] = datetime.now().isoformat()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/log-error", methods=["POST"])
def log_error():
    try:
        data = request.get_json()
        error_message = data.get("error")
        
        # Get session ID and user ID for tracking
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id(session)

        # Generate a unique error code
        error_id = f"ERR-{uuid.uuid4().hex[:8]}"
        
        # Log error to experiment data for research tracking
        if user_id:
            experiment_data = ExperimentData(
                session_id=session_id,
                user_id=user_id,
                user_action="code_error",
                participant_code=session.get('participant_code', 'unknown'),
                timestamp=datetime.now(),
                data=json.dumps({
                    "error_id": error_id,
                    "error_message": error_message,
                    "error_type": "javascript_runtime_error"
                })
            )
            # Only commit to DB if not in development mode
            if not is_development_mode():
                db.session.add(experiment_data)
                db.session.commit()
            else:
                print("[DEV] Skipping DB commit for experiment_data (development mode)")
        
        return jsonify({"success": True, "error_id": error_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

import re
# ...existing code...

@application.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        data = request.get_json()
        context = data.get("context", [])
        print(f"Application.py: Context received: {context}")
        user_message = data.get("input", "")
        extended_thinking = data.get("extended_thinking", False)
        session_id = session.get('session_id', f"session_{uuid.uuid4().hex[:12]}")
        if 'session_id' not in session:
            session['session_id'] = session_id
        user_id = session.get('user_id')
        response = ""
        if extended_thinking:
            response = assistant.get_react_response(context, user_message, session_id, user_id)
        else:
            response = assistant.get_llm_response(context, user_message, session_id, user_id)

        # Save user message and LLM response to ExperimentData
        if user_id:
            db.session.add(ExperimentData(
                session_id=session_id,
                user_id=user_id,
                participant_code=session.get('participant_code', 'unknown'),
                user_action="llm_message",
                timestamp=datetime.now(),
                data=json.dumps({
                    "user_message": user_message,
                    "llm_response": response,
                    "extended_thinking": extended_thinking
                })
            ))
            db.session.commit()
        session['last_ai_usage'] = datetime.now().isoformat()

        segments = []
        # Pattern matches ```lang\ncode``` or ```\ncode```
        pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        last_end = 0
        for match in pattern.finditer(response):
            # Add preceding text, if any
            if match.start() > last_end:
                text = response[last_end:match.start()].strip()
                if text:
                    segments.append(["text", text])
            code = match.group(2).strip()
            #lang = match.group(1) or ""
            segments.append(["code", code])
            last_end = match.end()
        # Add any trailing text
        if last_end < len(response):
            text = response[last_end:].strip()
            if text:
                segments.append(["text", text])
        if not segments:
            segments.append(["text", response])
            
        print(f"Application.py: Segments created: {segments}")
        print(jsonify(segments))

        return jsonify(segments)
    except Exception as e:
        return jsonify(["text", text])
    
@application.route("/sus", methods=["GET", "POST"])
def sus():
    if request.method == "GET":
        # Show SUS questionnaire
        return render_template('sus.html')
    
    elif request.method == "POST":
        try:
            session_id = session.get('session_id', 'unknown')
            user_id = get_int_user_id(session)
            
            if not user_id:
                user_id = 10000000001            
            # Get responses (1-5 scale)
            responses = []
            for i in range(1, 11):
                response = request.form.get(f'q{i}', type=int)
                if response is None or response < 1 or response > 5:
                    return jsonify({"success": False, "error": f"Invalid response for question {i}"}), 400
                responses.append(response)
            
            # Save to database
            sus_data = SUS(
                session_id=session_id,
                user_id=user_id,
                participant_code=session.get('participant_code', 'unknown'),
                q1_use_frequently=responses[0],
                q2_unnecessarily_complex=responses[1],
                q3_easy_to_use=responses[2],
                q4_need_technical_support=responses[3],
                q5_functions_integrated=responses[4],
                q6_too_much_inconsistency=responses[5],
                q7_learn_quickly=responses[6],
                q8_cumbersome_to_use=responses[7],
                q9_felt_confident=responses[8],
                q10_learn_lot_before_use=responses[9],
                submitted_at=datetime.now()
            )
            
            if not is_development_mode():
                db.session.add(sus_data)
                db.session.commit()
            
            # Redirect to debrief
            return redirect(url_for('debrief'))
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        
@application.route("/debrief", methods=["GET", "POST"])
def debrief():
    # Track experiment completion
    session_id = session.get('session_id', 'unknown')
    user_id = get_int_user_id(session)
    # Show participant code if available
    participant_code = None
    # Always try to get from session first
    participant_code = session.get('participant_code')
    # If not in session, try to get from user in DB
    if not participant_code and user_id:
        user = User.query.get(user_id)
        if user:
            participant_code = user.participant_code
            
    user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
    try:
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
            print(f"Deleted user game.js file: {user_file_path}")
    except Exception as e:
        print(f"Error deleting user game.js file: {e}")

    return render_template('debrief.html', participant_code=participant_code)

@application.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear current session conversation"""
    session_id = session.get('session_id')
    if session_id:
        assistant.clear_conversation(session_id)
        return jsonify({"success": True, "message": "Session cleared"})
    return jsonify({"success": False, "error": "No active session"})

@application.route("/save-final-game-code", methods=["POST"])
def save_final_game_code():
    """Save the user's final game.js script to the database at experiment completion."""
    try:
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "No user_id in session"}), 400
        user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
        if not os.path.exists(user_file_path):
            return jsonify({"success": False, "error": "User game.js file not found"}), 404
        with open(user_file_path, "r", encoding="utf-8") as f:
            code = f.read()
        experiment_data = ExperimentData(
            session_id=session_id,
            user_id=user_id,
            user_action="final_code_save",
            timestamp=datetime.now(),
            data=json.dumps({
                "file_name": f"game_{session_id}.js",
                "final_code": code,
                "code_length": len(code),
                "lines_count": len(code.split('\n'))
            })
        )
        if not is_development_mode():
            db.session.add(experiment_data)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for final_code_save (development mode)")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/get-user-game-code", methods=["GET"])
def get_user_game_code():
    """Get user-specific game code"""
    try:
        session_id = session.get('session_id', 'unknown')
        user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
        
        # If user file doesn't exist, copy from template
        if not os.path.exists(user_file_path):
            template_path = os.path.join(application.static_folder, "js", "game.js")
            os.makedirs(os.path.dirname(user_file_path), exist_ok=True)
            
            with open(template_path, "r", encoding="utf-8") as template_file:
                template_content = template_file.read()
            
            with open(user_file_path, "w", encoding="utf-8") as user_file:
                user_file.write(template_content)
        
        with open(user_file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        return jsonify({"success": True, "code": code})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/submit_survey", methods=["POST"])
def submit_survey():
    try:
        session_id = session.get('session_id', 'unknown')
        anon_user = session.get('anonymous_user', {})
        participant_code = anon_user.get('participant_code')
        signed_date = anon_user.get('signed_date')

        game_dev_experience_level = request.form.get('game_dev_experience_detailed')
        game_dev_proffessional_level = request.form.get('gamedev_position')
        game_dev_experience_years = request.form.get('gamedev_years', type=float)
        game_engines = request.form.getlist('engines')
        
        programming_experience_level = request.form.get('programming_experience_detailed')
        programming_proffessional_level = request.form.get('programming_position')
        programming_experience_years = request.form.get('programming_years', type=float)
        programming_languages = request.form.getlist('languages')
        
        used_phaser = request.form.get('used_phaser') == 'yes'
        uses_ai_tools = request.form.get('uses_ai_tools') == 'yes'
        ai_usage_details = request.form.getlist('ai_usage')
        
        # Student/graduate/self-taught fields
        is_student = bool(request.form.get('is_student'))
        is_graduate = bool(request.form.get('is_graduate'))
        is_self_taught = bool(request.form.get('is_self_taught'))
        self_taught_experience = request.form.getlist('self_taught_experience')
        degree_level_current = request.form.get('degree_level_current')
        degree_level_highest = request.form.get('degree_level_highest')
        course_programming_experience = request.form.getlist('course_programming_experience')
        undergrad_year = request.form.get('undergrad_year')
        course_related = request.form.get('course_related') == 'yes'

        # Save to database with session tracking
        survey_data = Survey(
            session_id=session_id,
            participant_code=participant_code,
            game_dev_experience_level=game_dev_experience_level,
            game_dev_proffessional_level=game_dev_proffessional_level,
            game_dev_experience_years=game_dev_experience_years,
            game_engines=json.dumps(game_engines) if game_engines else '',
            programming_experience_years=programming_experience_years,
            programming_experience_level=programming_experience_level,
            programming_proffessional_level=programming_proffessional_level,
            programming_languages=json.dumps(programming_languages) if programming_languages else '',
            used_phaser=used_phaser,
            uses_ai_tools=uses_ai_tools,
            ai_usage_details=json.dumps(ai_usage_details) if ai_usage_details else '',
            is_student=is_student,
            is_graduate=is_graduate,
            is_self_taught=is_self_taught,
            self_taught_experience=json.dumps(self_taught_experience) if self_taught_experience else '',
            degree_level_current=degree_level_current,
            degree_level_highest=degree_level_highest,
            course_programming_experience=json.dumps(course_programming_experience) if course_programming_experience else '',
            course_related=course_related,
            undergrad_year=undergrad_year,
            submitted_at=datetime.now(),
            description=request.form.get('description', '')
        )
        
        expertise = categorize_expertise_from_existing_survey(survey_data)
        assigned_condition = assign_balanced_condition(User, expertise)

        # Create the user in the database
        user = User(
            participant_code=participant_code,
            assigned_condition=assigned_condition,
            expertise_level=expertise,
            signed_date=signed_date
            )
        
        if not is_development_mode():
            db.session.add(user)
            db.session.commit()
            survey_data.user_id = user.id  # Link survey data to user
            db.session.add(survey_data)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for survey (development mode)")
        # Redirect to tutorial page instead of experiment
        return redirect(url_for('tutorial'))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/get-session-id", methods=["GET"])
def get_session_id():
    """Get current session ID for client-side tracking"""
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
        session_id = session['session_id']
    
    return jsonify({"session_id": session_id})

@application.route("/log-consent", methods=["POST"])
def log_consent():
    """Log consent decision with session tracking and create user in DB here"""
    try:
        print("Logging consent...")
        signed_date_form = request.form.get('date', datetime.now().isoformat())
        participant_code_val = session.get('participant_code')
        if not participant_code_val:
            participant_code_val = f"P{uuid.uuid4().hex[:8].upper()}"
            session['participant_code'] = participant_code_val
        # Store the user object in the session for use on the survey page
        session['anonymous_user'] = {
            'participant_code': participant_code_val,
            'signed_date': signed_date_form
        }
        session['user_id'] = None
        return redirect(url_for('survey'))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def check_auth(username, password):
    # Set your admin username and password here (or load from env)
    return username == 'admin' and password == 'yourpassword'

def authenticate():
    return Response(
        'Could not verify your access to this page.\n'
        'You must provide valid credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@application.route("/init-db")
#@requires_auth
def init_database():
    """Initialize database tables - REMOVE THIS ROUTE AFTER USE"""
    try:
        print("Creating database tables...")
        db.drop_all()  # Drop existing tables first
        db.create_all()
        print("Database tables created successfully!")
        return """
        <html>
        <head><title>Database Initialized</title></head>
        <body>
            <h1>Database Initialized Successfully</h1>
            <p>All database tables have been created.</p>
            <a href="/">Go to main site</a>
        </body>
        </html>
        """
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        traceback.print_exc()
        return f"""
        <html>
        <head><title>Database Error</title></head>
        <body>
            <h1>Database Initialization Failed</h1>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """, 500

@application.route("/tutorial")
def tutorial():
    return render_template('tutorial.html')

@application.route("/start-experiment", methods=["GET", "POST"])
def start_experiment():
    return redirect(url_for('gameAIassistant'))

@application.route('/log-task-check', methods=['POST'])
def log_task_check():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        user_id = session.get('user_id')
        session_id = session.get('session_id', 'unknown')
        if not user_id:
            return jsonify({'success': False, 'error': 'No user_id in session'}), 400
        task_check = TaskCheck(
            user_id=user_id,
            session_id=session_id,
            participant_code=session.get('participant_code', 'unknown'),
            task_id=task_id,
        )
        db.session.add(task_check)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@application.route("/log-game-reload", methods=["POST"])
def log_game_reload():
    """Log when the user reloads the game window."""
    try:
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id(session)
        timestamp = datetime.now()
        db_entry = ExperimentData(
            session_id=session_id,
            user_id=user_id,
            participant_code=session.get('participant_code', 'unknown'),
            user_action="game_reload",
            timestamp=timestamp,
            data=json.dumps({
                "message": "Game window reloaded",
                "timestamp": timestamp.isoformat()
            })
        )
        if not is_development_mode():
            db.session.add(db_entry)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for game_reload (development mode)")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/log-experiment-leave", methods=["POST"])
def log_experiment_leave():
    """Save the user's final game.js script to the database when the user leaves the experiment page."""
    try:
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id(session)
        if not user_id:
            return jsonify({"success": False, "error": "No user_id in session"}), 400
        user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
        if not os.path.exists(user_file_path):
            return jsonify({"success": False, "error": "User game.js file not found"}), 404
        with open(user_file_path, "r", encoding="utf-8") as f:
            code = f.read()
        experiment_data = ExperimentData(
            session_id=session_id,
            user_id=user_id,
            user_action="final_code_save",
            timestamp=datetime.now(),
            data=json.dumps({
                "file_name": f"game_{session_id}.js",
                "final_code": code,
                "code_length": len(code),
                "lines_count": len(code.split('\n'))
            })
        )
        if not is_development_mode():
            db.session.add(experiment_data)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for final_code_save (development mode)")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=False, port=5001)