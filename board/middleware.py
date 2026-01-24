from .metrics import agro_requests_total

class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        agro_requests_total.inc()
        return response
