from waitress import serve
from werkzeug.serving import run_simple

from main import application
from config import debug
if debug:
	run_simple('0.0.0.0', 8081, application, use_debugger=True, use_reloader=True)
else:
	serve(application, listen='*:8080')