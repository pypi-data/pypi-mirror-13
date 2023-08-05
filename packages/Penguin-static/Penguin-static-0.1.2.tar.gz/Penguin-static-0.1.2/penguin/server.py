import os
import threading
import http.server
import socketserver


class Server:

    def __init__(self, site):
        self.Port = site.Port
        if os.path.isdir(site.dest):
            self.Handler = http.server.SimpleHTTPRequestHandler
            self.httpd = socketserver.TCPServer(("", self.Port), self.Handler)
            try:
                t = threading.Thread(target=self.serve, args=(site,))
                t.start()
            except KeyboardInterrupt:
                self.httpd.shutdown()

    def serve(self, site):
        os.chdir(site.dest)
        print("Serving to port", self.Port)
        self.httpd.serve_forever()
