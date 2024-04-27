import json
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            body = request.body.decode('utf-8')
        except UnicodeDecodeError:
            body = 'Could not decode body'
        print(f"Request {request.method} {request.path}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {body}")
        return None
