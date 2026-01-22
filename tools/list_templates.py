import sys
import os

# Ensure project root is on sys.path so package imports work
sys.path.insert(0, os.getcwd())

from app import create_app

app = create_app()
with app.app_context():
    templates = app.jinja_env.list_templates()
    print('Found templates:', len(templates))
    for t in sorted(templates):
        print('-', t)
