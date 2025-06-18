from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os 
import webbrowser
from datetime import datetime
import assistant
import re
import esprima  # This actually works

class SimpleSecurityValidator:
    def __init__(self):
        # These patterns actually work and are tested
        self.critical_patterns = [
            r'\beval\s*\(',
            r'\bnew\s+Function\s*\(',
            r'\bsetTimeout\s*\(\s*[\'"`]',
            r'\bsetInterval\s*\(\s*[\'"`]'
        ]
    
    def validate(self, code):
        violations = []
        
        # 1. Basic pattern matching (fast, reliable)
        for pattern in self.critical_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(f"Dangerous pattern detected: {pattern}")
        
        # 2. AST parsing (this actually works with esprima)
        try:
            ast = esprima.parseScript(code)
            ast_violations = self._check_ast(ast)
            violations.extend(ast_violations)
        except Exception as e:
            violations.append(f"Code parsing failed: {str(e)}")
        
        return {
            'is_safe': len(violations) == 0,
            'violations': violations
        }
    
    def _check_ast(self, ast):
        # Simple AST traversal that actually works
        violations = []
        
        def traverse(node):
            if isinstance(node, dict):
                if node.get('type') == 'CallExpression':
                    callee = node.get('callee', {})
                    if (callee.get('type') == 'Identifier' and 
                        callee.get('name') in ['eval', 'Function']):
                        violations.append(f"Dangerous function call: {callee.get('name')}")
                
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        traverse(value)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(ast)
        return violations

# This actually works in Flask
validator = SimpleSecurityValidator()

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
    print(f"Consent received: {consent}")  # Debugging line to check consent value
    print(f"signature: {request.form.get('signature')}")  # Debugging line to check signature value
    print(f"date: {request.form.get('date')}")  # Debugging line to check date value
    if consent == 'agree':
        return redirect(url_for('survey'))
    
@app.route("/survey")
def survey():
    return render_template('survey.html')

@app.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        #print("Received data:", data)  # Debugging line to check received data
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
        
        print(f"Code saved to {file_path}")  # Debugging line to confirm save location
        
        
        # Print a success message with the number of lines saved
        print(f"Successfully saved {len(code_lines)} lines of code to {file_name}")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/LLMrequest", methods=["POST"])
def LLMrequest():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging line to check received data
        code = data.get("code")
        
        # Print the code received
        print("Code received for LLM request:", code)
        
        # Here you would typically process the code with your LLM and return a response
        # For now, we will just return a dummy response
        
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
                    #code_blocks.append(p.split("javascript")[1].strip())
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
        
        print(type(response_segments))  # Ensure response is a string or dict as expected
        
        print("Response from LLM:", response_segments)  # Debugging line to check LLM response
        # response = {
        #     "message": "This is a dummy response from the LLM.",
        #     "code": code  # Echoing back the received code for demonstration
        # }
        
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
