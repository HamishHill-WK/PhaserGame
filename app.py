from flask import Flask, render_template
import os 
import webbrowser

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

@app.route("/")
def game():        
    return render_template('game.html')

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5001')
    #app.run(debug=True, port=5001)
    app.run(host='0.0.0.0', debug=True, port=5001)
