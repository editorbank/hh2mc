#!/bin/env python3

DEFAULT_HTTP_INTERFACE = ''
DEFAULT_HTTP_PORT = 80
DEFAULT_MEMCACHED_INTERFACE = '0.0.0.0'
DEFAULT_MEMCACHED_PORT = 11211

HEADER_KEY = 'Memcached-Key'
HEADER_VALUE = 'Memcached-Value'
HEADER_TIME = 'Memcached-Time'
DEFAULT_VALUE = '' # if not specified
DEFAULT_TIME = 0 # key lifetime in seconds, 0 - infinity

try:
    from http import server # Python 3
except ImportError:
    import SimpleHTTPServer as server # Python 2
import memcache
import sys

def item_default(o,i=0, default=None):
    try:
        return o[i]
    except:
    	return default

def int_default(s, default=None):
    try:
        return int(s)
    except:
    	return default

def parseUrl(url = '', default_host=DEFAULT_HTTP_INTERFACE, default_port=DEFAULT_HTTP_PORT):
    try:
      pasedUrl = url.split(':',1)
      host = item_default(pasedUrl, 0) or default_host
      port = int_default(item_default(pasedUrl, 1)) or default_port
      return (host, port)
    except:
      return (default_host, default_port)
  

class MemcachedHTTPRequestHandler(server.SimpleHTTPRequestHandler):

    def _return(self, status, content = '', headers = {}):
        bytes = content.encode()
        self.send_response(status)
        for k,v in headers.items():
        	self.send_header(k,v)
        self.send_header('Content-Length',len(bytes))
        self.end_headers()
        self.wfile.write(bytes)

    def do_GET(self):
        try:
            key = self.headers[HEADER_KEY]
            value = MEMCACHE_CLIENT.get(key)
            if value == None:
                return self._return(404)
            return self._return(200,headers={HEADER_VALUE:value})
        except:
            return self._return(500)

    def do_POST(self):
        try:
            key = self.headers[HEADER_KEY]
            value = self.headers[HEADER_VALUE] or DEFAULT_VALUE
            time = int_default(self.headers[HEADER_TIME]) or DEFAULT_TIME
            if not key or not MEMCACHE_CLIENT.set(key, value, time=time):
                return self._return(400)
            return self._return(200)
        except:
            return self._return(500)

if __name__ == '__main__':
    if '--help' == item_default(sys.argv,1):
        print(f'Use: {sys.argv[0]} [<http_interface>:<http_port>] [<memcached_interface>:<memcached_port>]')
        print(f'Default arguments: {DEFAULT_HTTP_INTERFACE}:{DEFAULT_HTTP_PORT} {DEFAULT_MEMCACHED_INTERFACE}:{DEFAULT_MEMCACHED_PORT}')
        sys.exit()

    HTTPServerUrl=item_default(sys.argv,1,f'{DEFAULT_HTTP_INTERFACE}:{DEFAULT_HTTP_PORT}')
    memcacheClientUrl=item_default(sys.argv,2,f'{DEFAULT_MEMCACHED_INTERFACE}:{DEFAULT_MEMCACHED_PORT}')
    MEMCACHE_CLIENT = memcache.Client([memcacheClientUrl], debug=1)
    httpd = server.HTTPServer(parseUrl(HTTPServerUrl), MemcachedHTTPRequestHandler)
    httpd.serve_forever()
