from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
import json
from datetime import datetime
import assistant
import secval
import uuid
from data import db, Survey, ExperimentData, User, configure_database, is_development_mode
from dotenv import load_dotenv 

load_dotenv()

validator = secval.SimpleSecurityValidator()

application = Flask(__name__)
application.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

# IMPORTANT: Initialize database with Flask app
try:
    configure_database(application)
    print("Database configured successfully!")
except Exception as e:
    print(f"Error configuring database: {e}")

def is_development_mode():
    """Return True if FLASK_ENV is set to 'development'."""
    return os.environ.get('FLASK_ENV', '').lower() == 'development'

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

def get_int_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    try:
        return int(user_id)
    except (ValueError, TypeError):
        return None

@application.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        code = data.get("code")
        session_id = session.get('session_id', 'unknown')
        user_id = get_int_user_id()
        
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
            # Only commit to DB if not in development mode
            if not is_development_mode():
                db.session.add(experiment_data)
                db.session.commit()
            else:
                print("[DEV] Skipping DB commit for experiment_data (development mode)")
        
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
        user_id = get_int_user_id()

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
            # Only commit to DB if not in development mode
            if not is_development_mode():
                db.session.add(experiment_data)
                db.session.commit()
            else:
                print("[DEV] Skipping DB commit for experiment_data (development mode)")
        
        return jsonify({"success": True, "error_id": error_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@application.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        data = request.get_json()
        context = data.get("context", [])
        print(f"Application.py: Context received: {context}")
        user_message = data.get("input", "")
        
        # Get or create session ID
        session_id = session.get('session_id', f"session_{uuid.uuid4().hex[:12]}")
        if 'session_id' not in session:
            session['session_id'] = session_id
        
        # Get user_id from session for tracking
        user_id = session.get('user_id')
        
        response = assistant.get_response(context, user_message, session_id, user_id)
        
        response_segments = {}
        
        # Extract code between triple backticks if present
        if "```" in response.output_text:
            # Find all code blocks
            code_blocks = []
            parts = response.output_text.split("```")
            
            for i, p in enumerate(parts):
                print(f"\n\nApplication.py: Part {i}: {p}\n\n")
                if "javascript" in p:
                    # If the part contains 'javascript', it's likely a code block
                    response_segments[i] = ["code", p.split("javascript")[1].strip()]
                elif "json" in p:
                    # If the part contains 'json', it's likely a code block
                    response_segments[i] = ["code", p.split("json")[1].strip()]
                    code_blocks.append(p.strip())
                elif "js" in p:
                    # If the part contains 'js', it's likely a code block
                    response_segments[i] = ["code", p.split("js")[1].strip()]
                    code_blocks.append(p.strip())
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
    user_id = get_int_user_id()
    
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
        # Only commit to DB if not in development mode
        if not is_development_mode():
            db.session.add(experiment_data)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for experiment_data (development mode)")
    
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
        user_id = get_int_user_id()  # Get anonymous user ID from consent
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
        # Only commit to DB if not in development mode
        if not is_development_mode():
            db.session.add(survey_data)
            db.session.commit()
        else:
            print("[DEV] Skipping DB commit for survey (development mode)")
        
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
        if consent_participate == 'yes':
            consent_participate = True
        consent_data = request.form.get('consent_data', False)
        if consent_data == 'yes':
            consent_data = True
        user_name = request.form.get('signature', '')
        signed_date_form = request.form.get('date', datetime.now().isoformat())
        anonymous_user = User(
            signed=user_name,
            consent_data=consent_data,
            consent_participate=consent_participate,
            participant_code=f"P{uuid.uuid4().hex[:8].upper()}",  # Anonymous participant code
            signed_date=signed_date_form
        )
        # Only commit to DB if not in development mode
        if not is_development_mode():
            db.session.add(anonymous_user)
            db.session.flush()  # Get the user ID without committing
            session['user_id'] = anonymous_user.id  # Store integer ID
            db.session.commit()  # Now commit
        else:
            print("[DEV] Skipping DB commit for anonymous user (development mode)")
            session['user_id'] = None
        return redirect(url_for('survey'))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Database initialization function
def init_db():
    """Initialize database tables"""
    with application.app_context():
        db.create_all()
        print("Database tables created successfully!")

# Add these routes to your application.py

@application.route("/init-db")
def init_database():
    """Initialize database tables - REMOVE THIS ROUTE AFTER USE"""
    try:
        print("Creating database tables...")
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
        import traceback
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

@application.route("/test-db")
def test_database():
    """Test database connection"""
    try:
        # Test basic connection
        result = db.session.execute('SELECT 1')
        
        # Test if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return jsonify({
            "success": True,
            "message": "Database connection successful",
            "tables": tables,
            "table_count": len(tables)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Add these debug routes to your application.py

@application.route("/debug-env")
def debug_environment():
    """Debug environment variables - REMOVE AFTER DEBUGGING"""
    try:
        db_vars = {}
        env_vars_to_check = [
            'RDS_HOSTNAME', 'RDS_PORT', 'RDS_DB_NAME', 
            'RDS_USERNAME', 'RDS_PASSWORD', 'DATABASE_URL',
            'EXPERIMENT_DATA_LINK', 'SQLALCHEMY_DATABASE_URI'
        ]
        
        for var in env_vars_to_check:
            value = os.environ.get(var)
            if value:
                if 'PASSWORD' in var or 'URI' in var:
                    # Mask sensitive data but show if it exists
                    db_vars[var] = f"SET (length: {len(value)})"
                else:
                    db_vars[var] = value
            else:
                db_vars[var] = "NOT SET"
        
        # Check application config
        app_config = {}
        if hasattr(application, 'config'):
            uri = application.config.get('SQLALCHEMY_DATABASE_URI')
            if uri:
                app_config['SQLALCHEMY_DATABASE_URI'] = f"SET (length: {len(uri)})"
            else:
                app_config['SQLALCHEMY_DATABASE_URI'] = "NOT SET"
        
        return f"""
        <html>
        <head><title>Environment Debug</title></head>
        <body>
            <h1>Environment Variables</h1>
            <h2>Database Environment Variables:</h2>
            <ul>
                {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in db_vars.items()])}
            </ul>
            
            <h2>Application Config:</h2>
            <ul>
                {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in app_config.items()])}
            </ul>
            
            <br>
            <a href="/test-basic-connection">Test Basic Connection</a>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

@application.route("/test-basic-connection")
def test_basic_connection():
    """Test the most basic database connection"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Get the database URI
        uri = application.config.get('SQLALCHEMY_DATABASE_URI')
        if not uri:
            return " No database URI configured", 500
        
        # Parse the URI
        parsed = urlparse(uri)
        
        connection_info = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:] if parsed.path else 'postgres',
            'user': parsed.username,
            'password_set': bool(parsed.password)
        }
        
        # Try to connect with psycopg2 directly
        conn = psycopg2.connect(
            host=connection_info['host'],
            port=connection_info['port'],
            database=connection_info['database'],
            user=connection_info['user'],
            password=parsed.password,
            connect_timeout=10,
            sslmode='require'
        )
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return f"""
        <html>
        <head><title>Connection Test</title></head>
        <body>
            <h1>Database Connection Successful!</h1>
            <h2>Connection Details:</h2>
            <ul>
                <li><strong>Host:</strong> {connection_info['host']}</li>
                <li><strong>Port:</strong> {connection_info['port']}</li>
                <li><strong>Database:</strong> {connection_info['database']}</li>
                <li><strong>User:</strong> {connection_info['user']}</li>
                <li><strong>Password Set:</strong> {connection_info['password_set']}</li>
            </ul>
            <h2>Database Version:</h2>
            <p>{version}</p>
            
            <br>
            <a href="/init-db-safe">Try Safe Database Init</a>
        </body>
        </html>
        """
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return f"""
        <html>
        <head><title>Connection Failed</title></head>
        <body>
            <h1>Database Connection Failed</h1>
            <h2>Error:</h2>
            <p>{str(e)}</p>
            <h2>Full Error Details:</h2>
            <pre>{error_details}</pre>
            
            <h2>Troubleshooting:</h2>
            <ul>
                <li>Check if database is configured in EB Console</li>
                <li>Verify security groups allow connections</li>
                <li>Ensure database is in same VPC as EB environment</li>
            </ul>
        </body>
        </html>
        """, 500

@application.route("/init-db-safe")
def init_database_safe():
    """Initialize database with better error handling"""
    try:
        # Test connection first
        db.session.execute('SELECT 1')
        print("Database connection test passed")
        
        # Create tables
        db.create_all()
        print("Database tables created")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return f"""
        <html>
        <head><title>Database Initialized</title></head>
        <body>
            <h1>Database Initialized Successfully!</h1>
            <h2>Created Tables:</h2>
            <ul>
                {''.join([f'<li>{table}</li>' for table in tables])}
            </ul>
            <p>Total tables: {len(tables)}</p>
            
            <br>
            <a href="/">Go to main site</a>
        </body>
        </html>
        """
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return f"""
        <html>
        <head><title>Database Init Failed</title></head>
        <body>
            <h1>Database Initialization Failed</h1>
            <h2>Error:</h2>
            <p>{str(e)}</p>
            <h2>Full Error Details:</h2>
            <pre>{error_details}</pre>
        </body>
        </html>
        """, 500

@application.route("/health-check")
def health_check():
    """Simple health check that shows if data exists"""
    try:
        user_count = User.query.count()
        survey_count = Survey.query.count()
        experiment_count = ExperimentData.query.count()
        
        # Get latest entries
        latest_user = User.query.order_by(User.signed_date.desc()).first()
        latest_survey = Survey.query.order_by(Survey.submitted_at.desc()).first()
        latest_experiment = ExperimentData.query.order_by(ExperimentData.timestamp.desc()).first()
        
        return jsonify({
            "status": "healthy",
            "database_connected": True,
            "counts": {
                "users": user_count,
                "surveys": survey_count,
                "experiments": experiment_count,
                "total": user_count + survey_count + experiment_count
            },
            "latest_activity": {
                "latest_user": latest_user.signed_date.isoformat() if latest_user else None,
                "latest_survey": latest_survey.submitted_at.isoformat() if latest_survey else None,
                "latest_experiment": latest_experiment.timestamp.isoformat() if latest_experiment else None
            },
            "has_data": (user_count + survey_count + experiment_count) > 0
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "database_connected": False,
            "error": str(e)
        }), 500
        
@application.route("/debug-network")
def debug_network():
    """Debug network connectivity to RDS"""
    import subprocess
    import socket
    
    try:
        db_host = "experiment-database.c7agayyc2qqp.eu-west-2.rds.amazonaws.com"
        db_port = 5432
        
        results = []
        
        # Test 1: Basic socket connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((db_host, db_port))
            sock.close()
            
            if result == 0:
                results.append("Socket connection: SUCCESS")
            else:
                results.append(f"Socket connection: FAILED (error code: {result})")
        except Exception as e:
            results.append(f"Socket connection: ERROR - {str(e)}")
        
        # Test 2: DNS resolution
        try:
            import socket
            ip = socket.gethostbyname(db_host)
            results.append(f"DNS resolution: {db_host} → {ip}")
        except Exception as e:
            results.append(f"DNS resolution: FAILED - {str(e)}")
        
        # Test 3: Ping test (if available)
        try:
            ping_result = subprocess.run(['ping', '-c', '1', '-W', '3', db_host], 
                                       capture_output=True, text=True, timeout=10)
            if ping_result.returncode == 0:
                results.append("Ping: SUCCESS")
            else:
                results.append("Ping: FAILED")
        except Exception as e:
            results.append(f"Ping: Not available - {str(e)}")
        
        # Test 4: Telnet-like test
        try:
            import telnetlib
            tn = telnetlib.Telnet()
            tn.open(db_host, db_port, timeout=5)
            tn.close()
            results.append("Telnet test: SUCCESS")
        except Exception as e:
            results.append(f"Telnet test: FAILED - {str(e)}")
        
        return f"""
        <html>
        <head><title>Network Debug</title></head>
        <body>
            <h1>Network Connectivity Test</h1>
            <h2>Target: {db_host}:{db_port}</h2>
            
            <h3>Test Results:</h3>
            <ul>
                {''.join([f'<li>{result}</li>' for result in results])}
            </ul>
            
            <h3>If All Tests Fail:</h3>
            <ul>
                <li>EB and RDS are in different VPCs</li>
                <li>RDS is in private subnets with no route to EB</li>
                <li>Network ACLs are blocking traffic</li>
                <li>RDS subnet routing is incorrect</li>
            </ul>
            
            <h3>Quick Solution:</h3>
            <p><a href="/use-external-db">Set up external database</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"Debug error: {str(e)}", 500

if __name__ == "__main__":
    #if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #    webbrowser.open('http://127.0.0.1:5001')
    application.run(host='0.0.0.0', debug=False, port=5001)