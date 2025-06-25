import logging
import time

logger = logging.getLogger('django_requests')

class RequestLoggerMiddleware:
    """
    Middleware для логирования всех HTTP-запросов и ответов во всех приложениях проекта.
    Логирует метод, путь, параметры GET/POST и статус ответа.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Логируем входящий запрос
        log_data = {
            'method': request.method,
            'path': request.path,
            'get_params': dict(request.query_params.items()) if hasattr(request, 'query_params') else dict(request.GET.items()),
            'post_params': dict(request.data.items()) if request.method in ['POST', 'PUT'] and hasattr(request, 'data') else dict(request.POST.items()),
            'user': request.user.username if request.user.is_authenticated else 'Anonymous'
        }
        logger.info(f"Incoming Request: {log_data}")

        start_time = time.perf_counter()

        # Получаем ответ
        response = self.get_response(request)

        end_time = time.perf_counter()

        # Логируем ответ
        duration = end_time - start_time
        logger.info(f"Response for {request.method} {request.path}: Status={response.status_code}, Duration={duration:.3f}s")
        return response

    def process_exception(self, request, exception):
        """
        Логирование исключений, если они возникли во время обработки запроса.
        """
        logger.error(f"Exception in {request.method} {request.path}: {str(exception)}")