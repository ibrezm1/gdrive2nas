#!/home/pi/Projects/py-drive/tvenv/bin/python
from waitress import serve
import flaskapp
serve(flaskapp.app, host='0.0.0.0', port=8080)

# https://www.devdungeon.com/content/run-python-wsgi-web-app-waitress