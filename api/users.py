from http.server import BaseHTTPRequestHandler
from datetime import datetime
import json

class handler(BaseHTTPRequestHandler):

  def do_HEAD(self):
    self._set_headers()
    return

  def do_GET(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')).encode())
    return

  def do_POST(self):
    self._set_headers()
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD': 'POST'}
    )
    foo = form.getvalue("foo"))
    out = json.dumps({'foo': foo, 'status': 'ok'})
    self.wfile.write(out)
    return

