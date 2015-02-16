from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse

import templates


class BannerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(path.query)
        categories = query.get('category[]')

        banner = self.server.banner_store.select_banner(categories)

        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()

        if banner is not None:
            self.wfile.write(templates.MAIN % {'url': banner.url})
        else:
            self.wfile.write(templates.ERROR)


class BannerServer(HTTPServer):
    def __init__(self, host, port, banner_store):
        HTTPServer.__init__(self, (host, port), BannerRequestHandler)
        self.banner_store = banner_store
