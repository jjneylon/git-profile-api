from service import app


class RequestContext:
    """ test request context decorator for testing routes """
    def __init__(self, path, method='GET', content_type='application/json'):
        self.path = path
        self.method = method
        self.content_type = content_type

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            context_kwargs = {'method': self.method, 'content_type': self.content_type}
            with app.test_request_context(self.path, **context_kwargs):
                func(*args, **kwargs)
        return wrapper
