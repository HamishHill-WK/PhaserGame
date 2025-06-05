from flask import Flask, render_template, request, jsonify
import os 
import webbrowser

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

@app.route("/")
def gameNoAIassistant():        
    return render_template('game-no-AI-assistant.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/save-code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        code = data.get("code")
        file_name = data.get("file")
        
        # Validate file name to prevent directory traversal
        if file_name != "game.js":
            return jsonify({"success": False, "error": "Invalid file name"})
        
        # Save the code
        file_path = os.path.join(app.static_folder, "js", file_name)
        with open(file_path, "w") as f:
            f.write(code)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', debug=True, port=5001)
