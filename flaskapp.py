from flask import Flask
# importing datetime module for now()
from datetime import datetime as dt
 

 
app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')

# https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask

@app.route("/")
def home():
    x = dt.now().isoformat()
    #print('Current ISO:', x)
    return "Hello, Current time is " + x

@app.route("/cat")
def cat():
    return render_template("home.html")

@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('reports', path)

# app.run(host='0.0.0.0', port=8080,debug=True)