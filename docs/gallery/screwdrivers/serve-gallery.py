from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
print('http://127.0.0.1:8770')
ThreadingHTTPServer(('127.0.0.1',8770),SimpleHTTPRequestHandler).serve_forever()
