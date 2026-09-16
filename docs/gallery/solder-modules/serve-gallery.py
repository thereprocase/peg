"""Serve a downloaded gallery on loopback only. Python 3, no dependencies."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import argparse,webbrowser

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=0,help='0 chooses an available port')
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    directory=Path(__file__).resolve().parent
    if not (directory/'index.html').exists():directory=directory.parent/'dist'
    if not (directory/'index.html').exists():parser.error('Keep this launcher beside the gallery index.html.')
    class Handler(SimpleHTTPRequestHandler):
        extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.js':'text/javascript','.glb':'model/gltf-binary','.step':'application/step'}
        def __init__(self,*a,**kw):super().__init__(*a,directory=str(directory),**kw)
        def do_GET(self):
            if self.path.split('?')[0]=='/api/candidate-votes':
                payload=b'{"error":"Local copy: shared voting is unavailable."}'
                self.send_response(503);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload);return
            super().do_GET()
        def do_POST(self):self.send_error(405,'This downloaded gallery is read-only')
    with ThreadingHTTPServer(('127.0.0.1',args.port),Handler) as server:
        url=f'http://127.0.0.1:{server.server_port}/index.html'
        print(url,flush=True);print('Local, read-only gallery. Press Ctrl+C to close.',flush=True)
        if not args.no_browser:webbrowser.open(url)
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':main()
