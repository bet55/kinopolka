from collections.abc import Awaitable, Callable
import logging
import secrets
import time

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse


logger = logging.getLogger(__name__)

TEA_CODE_KEY = "tea_code"  # имя и GET-параметра, и куки
TEA_CODE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # год
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
TEA_CODE_EXEMPT_PREFIXES = ("/boss/",)  # у админки своя авторизация


class TeaCodeMiddleware:
    """
    «Свой-чужой» без полноценной авторизации: изменяющие запросы (POST/PUT/PATCH/DELETE)
    проходят только с верным tea_code. Просмотр (GET) открыт всем.

    Код попадает к пользователю один раз — ссылкой вида https://kinopolka.com/?tea_code=XXX,
    middleware сверяет его с settings.TEA_CODE и кладёт в куку (HttpOnly, на год).
    Дальше браузер шлёт куку сам, JS ничего не знает про код.
    Смена TEA_CODE в start.sh разом отзывает все старые ссылки и куки.
    """

    async_capable = True
    sync_capable = True

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)
        if not settings.TEA_CODE:
            logger.warning("TEA_CODE не задан — изменяющие запросы никак не защищены")

    def __call__(self, request: HttpRequest) -> HttpResponse | Awaitable[HttpResponse]:
        if self.async_mode:
            return self.__acall__(request)
        return self._denied_response(request) or self._set_cookie(request, self.get_response(request))

    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        return self._denied_response(request) or self._set_cookie(request, await self.get_response(request))

    @staticmethod
    def _code_is_valid(code: str | None) -> bool:
        # compare_digest — сравнение за константное время; bytes, т.к. со строками
        # не-ASCII он кидает TypeError
        return bool(code) and secrets.compare_digest(code.encode(), settings.TEA_CODE.encode())

    def _denied_response(self, request: HttpRequest) -> JsonResponse | None:
        """403, если изменяющий запрос пришёл без верного кода. None — пропускаем."""
        if (
            not settings.TEA_CODE
            or request.method not in UNSAFE_METHODS
            or request.path.startswith(TEA_CODE_EXEMPT_PREFIXES)
        ):
            return None

        code = request.GET.get(TEA_CODE_KEY) or request.COOKIES.get(TEA_CODE_KEY)
        if self._code_is_valid(code):
            return None

        logger.warning(f"Запрос без верного tea_code отклонён: {request.method} {request.path}")
        return JsonResponse(
            {"error": "Изменения доступны только членам киноклуба (нет tea_code)"},
            status=403,
            json_dumps_params={"ensure_ascii": False},
        )

    def _set_cookie(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Верный код из GET-параметра запоминаем в куке — дальше браузер шлёт её сам."""
        code = request.GET.get(TEA_CODE_KEY)
        if settings.TEA_CODE and self._code_is_valid(code) and request.COOKIES.get(TEA_CODE_KEY) != code:
            response.set_cookie(
                TEA_CODE_KEY,
                code,
                max_age=TEA_CODE_COOKIE_MAX_AGE,
                httponly=True,
                secure=settings.SSL_REDIRECT,
                samesite="Lax",
            )
        return response


class RequestLoggerMiddleware:
    """
    Middleware для логирования всех HTTP-запросов и ответов во всех приложениях проекта.
    Логирует метод, путь, параметры GET/POST и статус ответа.
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Логируем входящий запрос
        log_data = {
            "method": request.method,
            "path": request.path,
            "get_params": (
                dict(request.query_params.items()) if hasattr(request, "query_params") else dict(request.GET.items())
            ),
            "post_params": (
                dict(request.data.items())
                if request.method in ["POST", "PUT"] and hasattr(request, "data")
                else dict(request.POST.items())
            ),
            "user": (request.user.username if request.user.is_authenticated else "Anonymous"),
        }
        logger.info(f"Incoming Request: {log_data}")

        start_time = time.perf_counter()

        # Получаем ответ
        response = self.get_response(request)

        end_time = time.perf_counter()

        # Логируем ответ
        duration = end_time - start_time
        logger.info(
            f"Response for {request.method} {request.path}: Status={response.status_code}, Duration={duration:.3f}s"
        )
        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> JsonResponse:
        """
        Логирование исключений, если они возникли во время обработки запроса.
        """
        logger.error(f"Exception in {request.method} {request.path}: {exception!s}")
        return JsonResponse(
            {"error": "ttt", "message": "usama", "exception": str(exception)},
            status=418,
            json_dumps_params={"ensure_ascii": False},
        )
