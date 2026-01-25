import logging
import time

logger = logging.getLogger("django.request")

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = round(time.time() - start, 3)

        logger.info(
            f'{request.method} {request.path} '
            f'status={response.status_code} '
            f'duration={duration}s'
        )

        return response
