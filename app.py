from flask import Flask, render_template, request, jsonify
import os 
import webbrowser

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

@app.route("/gamenoAIassistant")
def gameNoAIassistant():        
    return render_template('game-no-AI-assistant.html')

@app.route("/gameAIassistant")
def gameAIassistant():        
    return render_template('game-AI-assistant.html')

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        #print("Received data:", data)  # Debugging line to check received data
        code = data.get("code")
        
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

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', debug=True, port=5001)
