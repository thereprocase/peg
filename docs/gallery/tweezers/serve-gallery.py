from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
print('http://127.0.0.1:8771',flush=True)
ThreadingHTTPServer(('127.0.0.1',8771),SimpleHTTPRequestHandler).serve_forever()
