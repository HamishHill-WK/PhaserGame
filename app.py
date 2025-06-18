from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
from datetime import datetime
import assistant
import secval

# This actually works in Flask
validator = secval.SimpleSecurityValidator()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

@app.route("/openexperiment", methods=["GET", "POST"])
def openexperiment():
    return redirect(url_for('gameAIassistant'))

@app.route("/gameAIassistant", methods=["GET", "POST"])
def gameAIassistant():        
    return render_template('game-AI-assistant.html')

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

# Add the survey route
@app.route("/opensurvey", methods=["GET", "POST"])
def opensurvey():
    consent = request.form.get('consent')
    if consent == 'agree':
        return redirect(url_for('survey'))
    
@app.route("/survey")
def survey():
    return render_template('survey.html')

@app.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        code = data.get("code")
        
        # Validate code safety
        is_safe, message = validator.validate(code)
        if not is_safe:
            return jsonify({"success": False, "error": f"Security violation: {message}"})
        
        #print("Code to save:", code)  # Debugging line to check code content
        code_lines = code.split('\n')
        print(f"Number of lines: {len(code_lines)}")

        file_name = data.get("file")
        
        # Validate file name to prevent directory traversal
        if file_name != "game.js":
            return jsonify({"success": False, "error": "Invalid file name"})

        # Save the code
        file_path = os.path.join(app.static_folder, "js", file_name)
        with open(file_path, "w", encoding="utf-8", newline='') as f:
            f.write(code)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        response = assistant.get_response().output_text  # Assuming this function interacts with the LLM
        
        response_segments = {}
        
        # Extract code between triple backticks if present
        if "```" in response:
            # Find all code blocks
            code_blocks = []
            parts = response.split("```")
            
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
                
        reponse_list = list(response_segments.values())
        
        return jsonify(reponse_list)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/debrief", methods=["GET", "POST"])
def debrief():
    return render_template('debrief.html')

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', debug=True, port=5001)
