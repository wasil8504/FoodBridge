import urllib.request
import urllib.error
import sys
try:
    response = urllib.request.urlopen('http://127.0.0.1:8001/', timeout=5)
    print('Status:', response.status)
    sys.exit(0)
except Exception as e:
    print('Error:', e)
    sys.exit(1)
