"""WSGI entrypoint for Gunicorn, ensuring we load the root-level app.py rather than the app/ package.

Run:
  gunicorn -w 2 -b 0.0.0.0:5001 wsgi:app
"""

import os
import os.path as p
from importlib.machinery import SourceFileLoader

ROOT = p.dirname(p.abspath(__file__))
# Load the root-level app.py module (named root_app to avoid name conflicts)
root_app_mod = SourceFileLoader("root_app", p.join(ROOT, "app.py")).load_module()
app = root_app_mod.app
