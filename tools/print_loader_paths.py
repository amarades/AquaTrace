import sys, os
sys.path.insert(0, os.getcwd())
from app import create_app
app = create_app()
with app.app_context():
    loader = app.jinja_loader
    try:
        paths = loader.searchpath
    except Exception:
        paths = getattr(loader, 'loader', None)
    print('Jinja loader type:', type(loader))
    print('Search paths:')
    try:
        for p in loader.searchpath:
            print('-', p)
    except Exception as e:
        print('Could not read searchpath:', e)
