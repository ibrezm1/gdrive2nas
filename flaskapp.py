from flask import Flask, render_template
# importing datetime module for now()
from datetime import datetime as dt
import sqlite3 

 
app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='templates')

# https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask

@app.route("/")
def home():
    x = dt.now().isoformat()
    #print('Current ISO:', x)
    return "Hello, Current time is " + x

def get_db_connection():
    conn = sqlite3.connect('files.db')
    conn.row_factory = sqlite3.Row
    return conn

#@app.before_request
@app.route("/table")
def cat():
    conn = get_db_connection()
    items = conn.execute('SELECT COUNT(id),MAX(Created_time) FROM FILENAMES').fetchall()
    conn.close()
    return render_template('table.html',  items=items)

#@app.after_request


@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('reports', path)

# app.run(host='0.0.0.0', port=8080,debug=True)