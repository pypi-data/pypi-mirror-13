# coding: utf-8
from webob import Request, Response


class App(object):

    def __init__(self):
        self.afters = []
        self.befores = []
        self.views = []

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = None

        # match route or 404
        view_fn = self.get_view_for_route(request)
        if view_fn is None:
            response = Response()
            response.status_int = 404
            response.json = None
            return response(environ, start_response)

        # before middlewares
        for before in self.befores:
            response = before(request)
            if response is not None:
                return self.render_response(environ, start_response, response)

        # run view
        response = view_fn(request)
        if isinstance(response, dict):
            response = Response(json=response)

        # after middlewares
        for after in self.afters:
            a_response = after(request, response)
            if a_response is not None:
                return self.render_response(environ, start_response, response)

        # Support dict as view/middleware response
        return self.render_response(environ, start_response, response)

    def render_response(self, environ, start_response, response):
        if isinstance(response, dict):
            response = Response(json=response)
        return response(environ, start_response)

    def after(self, after_fn):
        self.afters.append(after_fn)
        def decorator(*args, **kwargs):
            return after_fn(*args, **kwargs)
        return decorator

    def before(self, before_fn):
        self.befores.append(before_fn)
        def decorator(*args, **kwargs):
            return before_fn(*args, **kwargs)
        return decorator

    def get_view_for_route(self, request):
        views = list(filter(lambda x: request.path == x.punch_path, self.views))
        if not views:
            return
        # views = list(filter(lambda x: (x.punch_methods and request.method in x.punch_methods), views))
        # if not views:
        #     return
        return views[0]

    def serve(self, server=None):
        """Serve app using wsgiref or provided server.

        Args:
        - server (callable): An callable
        """
        if server is None:
            from wsgiref.simple_server import make_server
            server = lambda app: make_server('', 8000, app).serve_forever()
            print('Listening on 0.0.0.0:8000')
        try:
            server(self)
        finally:
            server.socket.close()

    def view(self, path='', methods=None, **kwargs):
        def decorator(view_fn):
            view_fn.punch_path = path
            view_fn.punch_methods = methods
            view_fn.punch_kwargs = kwargs
            self.views.append(view_fn)
            return view_fn
        return decorator
