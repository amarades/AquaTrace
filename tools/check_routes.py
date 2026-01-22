import urllib.request
import urllib.error

urls = [
    'http://127.0.0.1:5000/',
    'http://127.0.0.1:5000/login',
    'http://127.0.0.1:5000/signup',
    'http://127.0.0.1:5000/some-nonexistent-page'
]

for u in urls:
    print('\n===', u, '===')
    try:
        with urllib.request.urlopen(u, timeout=5) as r:
            print('Status:', r.status)
            ct = r.getheader('Content-Type')
            print('Content-Type:', ct)
            data = r.read(300)
            print('Body (first 300 chars):\n')
            print(data.decode('utf-8', 'replace'))
    except urllib.error.HTTPError as e:
        print('HTTPError:', e.code)
        try:
            err_body = e.read()
            print('Error body:')
            print(err_body.decode('utf-8', 'replace'))
        except Exception as ex:
            print('Failed to read error body:', ex)
    except Exception as e:
        print('ERROR:', type(e).__name__, e)
