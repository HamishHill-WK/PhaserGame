from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
import json
from datetime import datetime
import assistant
import secval
import uuid
from data import Survey, ExperimentData, User, configure_database
from dotenv import load_dotenv 

load_dotenv()

print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"SECRET_KEY: {os.environ.get('SECRET_KEY', 'NOT SET')}")
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
print("=" * 50)

validator = secval.SimpleSecurityValidator()

application = Flask(__name__)
application.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
#db = configure_database(application)

errors = []

@application.route("/gameAIassistant", methods=["GET", "POST"])
def gameAIassistant():
    # Use existing session ID from survey flow or create new one
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    return render_template('game-AI-assistant.html')

@application.route("/")
@application.route("/index")
def index():
    # Generate session ID for user tracking across all pages
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    return render_template('index.html')

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
        data = request.get_json()
        code = data.get("code")
        
        # Get session ID and user ID for tracking
        session_id = session.get('session_id', 'unknown')
        user_id = session.get('user_id')
        
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
            return jsonify({"success": False, "error": "Invalid file name"})

        # Save to user-specific file
        user_file_path = os.path.join(application.static_folder, "js", "users", f"game_{session_id}.js")
        os.makedirs(os.path.dirname(user_file_path), exist_ok=True)
        
        with open(user_file_path, "w", encoding="utf-8", newline='') as f:
            f.write(code)
        
        # Log code save action to experiment data
        if user_id:
            experiment_data = ExperimentData(
                session_id=session_id,
                user_id=user_id,
                user_action="code_save",
                timestamp=datetime.now(),
                data=json.dumps({
                    "file_name": file_name,
                    "code_length": len(code),
                    "lines_count": len(code_lines)
                })
            )
            #db.session.add(experiment_data)
            #db.session.commit()
        
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
        user_id = session.get('user_id')
        
        # Generate a unique error code
        error_id = f"ERR-{uuid.uuid4().hex[:8]}"

        # Add error_id to the error data
        data["error_id"] = error_id
        
        # Log the error message
        errors.append({
            "error_id": error_id,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Log error to experiment data for research tracking
        if user_id:
            experiment_data = ExperimentData(
                session_id=session_id,
                user_id=user_id,
                user_action="code_error",
                timestamp=datetime.now(),
                data=json.dumps({
                    "error_id": error_id,
                    "error_message": error_message,
                    "error_type": "javascript_runtime_error"
                })
            )
            
            #if(db.session.is_active):
                #db.session.add(experiment_data)
                #db.session.commit()
            
        return jsonify({"success": True, "error_id": error_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        data = request.get_json()
        user_message = data.get("input", "")
        
        # Get or create session ID
        session_id = session.get('session_id', f"session_{uuid.uuid4().hex[:12]}")
        if 'session_id' not in session:
            session['session_id'] = session_id
        
        # Get user_id from session for tracking
        user_id = session.get('user_id')
        
        response = assistant.get_response(user_message, session_id, user_id)
        
        response_segments = {}
        
        # Extract code between triple backticks if present
        if "```" in response.output_text:
            # Find all code blocks
            code_blocks = []
            parts = response.output_text.split("```")
            
            for i, p in enumerate(parts):
                if "javascript" in p:
                    # If the part contains 'javascript', it's likely a code block
                    response_segments[i] = ["code", p.split("javascript")[1].strip()]
                else:
                    # Otherwise, it's just a regular text segment
                    response_segments[i] = ["text", p.strip()]
            
            # If we found code blocks, update the response
            if code_blocks:
                response = {
                    "message": response_segments,
                    "code": code_blocks
                }
        else:
            # If no code blocks, just return the text response
            response_segments[0] = ["text", response.output_text]
                
        reponse_list = list(response_segments.values())
        
        return jsonify(reponse_list)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/debrief", methods=["GET", "POST"])
def debrief():
    # Track experiment completion
    session_id = session.get('session_id', 'unknown')
    user_id = session.get('user_id')
    
    if user_id and request.method == "GET":
        # Log that user reached debrief (experiment completion)
        experiment_data = ExperimentData(
            session_id=session_id,
            user_id=user_id,
            user_action="experiment_completed",
            timestamp=datetime.now(),
            data=json.dumps({
                "reached_debrief": True,
                "completion_timestamp": datetime.now().isoformat()
            })
        )
        #db.session.add(experiment_data)
        #db.session.commit()
    
    return render_template('debrief.html')

@application.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear current session conversation"""
    session_id = session.get('session_id')
    if session_id:
        assistant.clear_conversation(session_id)
        return jsonify({"success": True, "message": "Session cleared"})
    return jsonify({"success": False, "error": "No active session"})

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
        # Get session ID to link survey to user journey
        session_id = session.get('session_id', 'unknown')
        user_id = session.get('user_id')  # Get anonymous user ID from consent
        print(f"Session ID: {session_id}, User ID: {user_id}")
        # Ensure user has given consent
        if not user_id:
            return jsonify({"success": False, "error": "Consent required before submitting survey"})
        
        # Get form data
        game_dev_experience_description = request.form.get('gamedev_details')
        game_dev_experience_level = request.form.get('game_dev_experience_detailed')
        game_dev_proffessional_level = request.form.get('gamedev_position')
        game_dev_experience_years = request.form.get('gamedev_years', type=float)
        game_engines = request.form.getlist('engines')  # Multiple selections
        
        programming_experience_level = request.form.get('programming_experience_detailed')
        programming_proffessional_level = request.form.get('programming_position')
        programming_experience_description = request.form.get('programming_details')
        programming_experience_years = request.form.get('programming_years', type=float)
        programming_languages = request.form.getlist('languages')  # Multiple selections
        used_phaser = request.form.get('used_phaser') == 'yes'
        phaser_experience_description = request.form.get('phaser_details', '')  # Additional details
        uses_ai_tools = request.form.get('uses_ai_tools') == 'yes'
        ai_usage_details = request.form.getlist('ai_usage')
        ai_usage_description = request.form.get('ai_usage_details', '')  # Additional details
    
        # Save to database with session tracking
        survey_data = Survey(
            session_id=session_id,
            user_id=user_id,  # Link to anonymous user from consent
            game_dev_experience_description=game_dev_experience_description,
            game_dev_experience_level=game_dev_experience_level,
            game_dev_proffessional_level=game_dev_proffessional_level,
            game_dev_experience_years=game_dev_experience_years,
            game_engines=json.dumps(game_engines) if game_engines else '',  # Convert
            programming_experience_description=programming_experience_description,
            programming_experience_years=programming_experience_years,
            programming_experience_level=programming_experience_level,
            programming_proffessional_level=programming_proffessional_level,
            programming_languages=json.dumps(programming_languages) if programming_languages else '',  # Store as JSON string            
            used_phaser=used_phaser,
            phaser_experience_description=phaser_experience_description,
            uses_ai_tools=uses_ai_tools,
            ai_usage_details=ai_usage_details,
            ai_tools_description=ai_usage_description,
            submitted_at=datetime.now()
        )
        
        #db.session.add(survey_data)
        #db.session.commit()
        
        # Redirect to experiment page
        return redirect(url_for('gameAIassistant'))
        
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
    """Log consent decision with session tracking"""
    try:
        print("Logging consent...")
        session_id = session.get('session_id', 'unknown')
        consent_participate = request.form.get('consent_participate', False)
        consent_data = request.form.get('consent_data', False)
        user_name = request.form.get('user_name', '')
        signed_date_form = request.form.get('signed_date', datetime.now().isoformat())
          # Create anonymous user record for consent tracking
        anonymous_user = User(
            signed=user_name,
            consent_data=consent_data,
            consent_participate=consent_participate,
            participant_code=f"P{uuid.uuid4().hex[:8].upper()}",  # Anonymous participant code
            signed_date=signed_date_form
        )
        
        #db.session.add(anonymous_user)
        #db.session.flush()  # Get the user ID without committing
        
        print(f"Anonymous user created with ID: {anonymous_user.id}, Participant Code: {anonymous_user.participant_code}")

        # Store user ID in session for linking survey and experiment data
        session['user_id'] = anonymous_user.participant_code

        # return jsonify({
        #     "success": True, 
        #     "session_id": session_id,
        #     "participant_code": anonymous_user.participant_code
        # })
        return redirect(url_for('survey'))

        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Database initialization function
def init_db():
    """Initialize database tables"""
    with application.app_context():
        #db.create_all()
        print("Database tables created successfully!")

# Uncomment to initialize database on first run
#init_db()

if __name__ == "__main__":
    #if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #    webbrowser.open('http://127.0.0.1:5001')
    application.run(host='0.0.0.0', debug=False, port=5001)