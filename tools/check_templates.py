from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, TemplateNotFound
import os

paths = [
    os.path.join(os.getcwd(), 'app', 'templates'),
    os.path.join(os.getcwd(), 'templates')
]

env = Environment(loader=FileSystemLoader(paths))

templates = ['main.html', 'base.html', 'login.html', 'signup.html', 'dashboard.html', '404.html', '500.html']

for t in templates:
    print('\nChecking', t)
    try:
        tpl = env.get_template(t)
        print('OK')
    except TemplateSyntaxError as e:
        print('TemplateSyntaxError:', e.message)
        print('In file:', e.filename, 'line', e.lineno)
    except TemplateNotFound as e:
        print('TemplateNotFound')
    except Exception as e:
        print('Other error:', type(e).__name__, e)
