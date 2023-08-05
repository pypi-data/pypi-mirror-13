class Middleware(object):
    """WSGI middleware for Engine.IO.

    This middleware dispatches traffic to an Engine.IO application, and
    optionally forwards regular HTTP traffic to a WSGI application.

    :param engineio_app: The Engine.IO server.
    :param wsgi_app: The WSGI app that receives all other traffic.
    :param engineio_path: The endpoint where the Engine.IO application should
                          be installed. The default value is appropriate for
                          most cases.

    Example usage::

        import engineio
        import eventlet
        from . import wsgi_app

        eio = engineio.Server()
        app = engineio.Middleware(eio, wsgi_app)
        eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
    """
    def __init__(self, engineio_app, wsgi_app=None, engineio_path='engine.io'):
        self.engineio_app = engineio_app
        self.wsgi_app = wsgi_app
        self.engineio_path = engineio_path

    def __call__(self, environ, start_response):
        if 'gunicorn.socket' in environ:
            # gunicorn saves the socket under environ['gunicorn.socket'], while
            # eventlet saves it under environ['eventlet.input']. Eventlet also
            # stores the socket inside a wrapper class, while gunicon writes it
            # directly into the environment. To give eventlet's WebSocket
            # module access to this socket when running under gunicorn, here we
            # copy the socket to the eventlet format.
            class Input(object):
                def __init__(self, socket):
                    self.socket = socket

                def get_socket(self):
                    return self.socket

            environ['eventlet.input'] = Input(environ['gunicorn.socket'])
        path = environ['PATH_INFO']
        if path is not None and \
                path.startswith('/{0}/'.format(self.engineio_path)):
            return self.engineio_app.handle_request(environ, start_response)
        elif self.wsgi_app is not None:
            return self.wsgi_app(environ, start_response)
        else:
            start_response("404 Not Found", [('Content-type', 'text/plain')])
            return ['Not Found']
