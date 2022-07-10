import http.server, argparse, hashlib, random, os, string, ssl, sys
import _root
import _folder, _helper

HOST_NAME = ''
DEFAULT_PORT = 3007



def main(*, port=DEFAULT_PORT, httpsfiles=None, extension=None, delay=None, disable_logging=None):
    if extension:
        if not os.path.exists(extension):
            _helper.errorExit('extension folder does not exist: ' + extension)

        print('loading extension ' + extension)
        sys.path.append(extension)
        from extension import ExtensionSignaserverHandler as Handler

    else:
        print('no extension loaded')
        from signaserver_handler import SignaserverHandler as Handler



    if delay:
        Handler._debug_delay = delay / 1000.0

    if disable_logging:
        Handler._disable_logging = True



    class HTTPServer(http.server.HTTPServer):
        _rnd = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        def get_request(self):
            req = http.server.HTTPServer.get_request(self)
            return req[0], (hashlib.sha1((HTTPServer._rnd + req[1][0]).encode('utf-8')).hexdigest(), req[1][1])

    #class ThreadedHTTPServer(HTTPServer):
    #    pass

    httpd = HTTPServer((HOST_NAME, port), Handler)

    if httpsfiles == None:
        protocol = 'http'
    else:
        protocol = 'https'

        certfile, keyfile = httpsfiles
        httpd.socket = ssl.wrap_socket(httpd.socket,
                                       server_side=True,
                                       certfile=certfile,
                                       keyfile=keyfile,
                                       ssl_version=ssl.PROTOCOL_TLS)

    print('%s://localhost:%d/signaclient.html' % (protocol, port))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run server.')
    parser.add_argument('--extension', type=str, help='Extension to load.', default=None)
    parser.add_argument('--delay', type=int, help='Additional delay to add in ms, for debugging.', default=None)
    parser.add_argument('--port', type=int, help='Port to use. (default %d).' % DEFAULT_PORT, default=DEFAULT_PORT)
    protocol_group = parser.add_mutually_exclusive_group(required=True)
    protocol_group.add_argument('--http', action='store_true', help='Run with http.')
    protocol_group.add_argument('--https', type=str, nargs=2, metavar=('CRT', 'KEY'), help='Run with https; specify path to crt file and key file.', default=None)
    args = parser.parse_args()

    main(port=args.port, httpsfiles=args.https, extension=args.extension, delay=args.delay)
