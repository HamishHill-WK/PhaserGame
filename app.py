from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
import json
from datetime import datetime
import assistant
import secval
import uuid
from data import Survey, ExperimentData, User, configure_database

# This actually works in Flask
validator = secval.SimpleSecurityValidator()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
db = configure_database(app)

errors = []

@app.route("/openexperiment", methods=["GET", "POST"])
def openexperiment():
    return redirect(url_for('gameAIassistant'))

@app.route("/gameAIassistant", methods=["GET", "POST"])
def gameAIassistant():
    # Use existing session ID from survey flow or create new one
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    return render_template('game-AI-assistant.html')

@app.route("/")
@app.route("/index")
def index():
    # Generate session ID for user tracking across all pages
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    return render_template('index.html')

# Add the survey route
@app.route("/opensurvey", methods=["GET", "POST"])
def opensurvey():
    # Ensure session ID exists from consent page
    if 'session_id' not in session:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
    
    consent = request.form.get('consent')
    if consent == 'agree':
        return redirect(url_for('survey'))
    
@app.route("/survey")
def survey():
    # Ensure session ID consistency
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
        session_id = session['session_id']
    
    return render_template('survey.html', session_id=session_id)

@app.route("/save-code", methods=["POST"])
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
        user_file_path = os.path.join(app.static_folder, "js", "users", f"game_{session_id}.js")
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
            db.session.add(experiment_data)
            db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/log-error", methods=["POST"])
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
            db.session.add(experiment_data)
            db.session.commit()
            
        return jsonify({"success": True, "error_id": error_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/LLMrequest", methods=["POST"])
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

@app.route("/debrief", methods=["GET", "POST"])
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
        db.session.add(experiment_data)
        db.session.commit()
    
    return render_template('debrief.html')

@app.route("/get-session-info", methods=["GET"])
def get_session_info():
    """Get current session information"""
    session_id = session.get('session_id', 'no_session')
    conversation_history = assistant.get_conversation(session_id)
    
    return jsonify({
        "session_id": session_id,
        "conversation_count": len(conversation_history),
        "has_conversation": len(conversation_history) > 0
    })

@app.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear current session conversation"""
    session_id = session.get('session_id')
    if session_id:
        assistant.clear_conversation(session_id)
        return jsonify({"success": True, "message": "Session cleared"})
    return jsonify({"success": False, "error": "No active session"})

@app.route("/get-user-game-code", methods=["GET"])
def get_user_game_code():
    """Get user-specific game code"""
    try:
        session_id = session.get('session_id', 'unknown')
        user_file_path = os.path.join(app.static_folder, "js", "users", f"game_{session_id}.js")
        
        # If user file doesn't exist, copy from template
        if not os.path.exists(user_file_path):
            template_path = os.path.join(app.static_folder, "js", "game.js")
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

@app.route("/submit-survey", methods=["POST"])
def submit_survey():
    try:
        # Get session ID to link survey to user journey
        session_id = session.get('session_id', 'unknown')
        user_id = session.get('user_id')  # Get anonymous user ID from consent
        
        # Ensure user has given consent
        if not user_id:
            return jsonify({"success": False, "error": "Consent required before submitting survey"})
        
        # Get form data
        game_dev_experience = request.form.get('game_dev_experience')
        programming_experience = request.form.get('programming_experience')
        languages = request.form.getlist('languages')  # Multiple selections
        uses_ai_tools = request.form.get('uses_ai_tools') == 'yes'
        ai_usage_details = request.form.get('ai_usage_details', '')
        
        # Save to database with session tracking
        survey_data = Survey(
            session_id=session_id,
            user_id=user_id,  # Link to anonymous user from consent
            game_dev_experience=game_dev_experience,
            programming_experience=programming_experience,
            languages=','.join(languages) if languages else '',  # Convert list to string
            uses_ai_tools=uses_ai_tools,
            ai_usage_details=ai_usage_details,
            submitted_at=datetime.now()
        )
        
        db.session.add(survey_data)
        db.session.commit()
        
        # Redirect to experiment page
        return redirect(url_for('gameAIassistant'))
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/get-session-id", methods=["GET"])
def get_session_id():
    """Get current session ID for client-side tracking"""
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = f"session_{uuid.uuid4().hex[:12]}"
        session_id = session['session_id']
    
    return jsonify({"session_id": session_id})

@app.route("/log-consent", methods=["POST"])
def log_consent():
    """Log consent decision with session tracking"""
    try:
        session_id = session.get('session_id', 'unknown')
        consent_given = request.json.get('consent_given', False)
        user_name = request.json.get('user_name', '')
          # Create anonymous user record for consent tracking
        anonymous_user = User(
            signed=user_name,
            participant_code=f"P{uuid.uuid4().hex[:8].upper()}",  # Anonymous participant code
            signed_date=datetime.now()
        )
        
        db.session.add(anonymous_user)
        db.session.flush()  # Get the user ID without committing
        
        # Store user ID in session for linking survey and experiment data
        session['user_id'] = anonymous_user.id
        

        return jsonify({
            "success": True, 
            "session_id": session_id,
            "participant_code": anonymous_user.participant_code
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Database initialization function
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

# Uncomment to initialize database on first run
# init_db()

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    app.run(host='0.0.0.0', debug=True, port=5001)