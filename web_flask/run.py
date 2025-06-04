import sys
if len(sys.argv) > 1 and sys.argv[1] == "web":
    from web_flask.app import app
    app.run(debug=True)
else:
    from gui_tkinter.main import run_gui
    run_gui()
from flask import Flask
from web_flask.routes.routes import budget_routes

app = Flask(__name__)
app.register_blueprint(budget_routes)

if __name__ == "__main__":
    app.run(debug=True)
