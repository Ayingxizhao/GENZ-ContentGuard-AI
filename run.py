"""Dev launcher for ContentGuard AI (Flask app).

Usage:
  python run.py

This runs the Flask development server. For production, prefer:
  gunicorn -w 2 -b 0.0.0.0:5001 wsgi:app
"""

import os
import os.path as p
from importlib.machinery import SourceFileLoader

# Explicitly load the root-level app.py to avoid conflict with the 'app/' package
ROOT = p.dirname(p.abspath(__file__))
app_module = SourceFileLoader("root_app", p.join(ROOT, "app.py")).load_module()
app = app_module.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
