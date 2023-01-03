from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import sys
class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers(self):
        # Для разрешения CROS.(Запросы от других url)
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPRequestHandler.end_headers(self)
test(
    CORSRequestHandler,
    HTTPServer,
    port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000,
)