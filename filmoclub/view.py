import logging
from typing import NoReturn

from asgiref.sync import async_to_sync
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token

from mixins import GlobalDataMixin


logger = logging.getLogger(__name__)

# ======================
# ОБРАБОТЧИКИ ОШИБОК
# requires_csrf_token не используется, но оставим на будущее
# ======================

ERROR_TEXTS = {
    400: "Неверный запрос",
    403: "Доступ запрещён",
    404: "Страница не найдена",
    500: "Ошибка сервера",
}


def is_media_or_static(request: HttpRequest) -> bool:
    """Проверяет, запрашивается ли статика или медиа"""
    path = request.path
    return path.startswith("/media") or path.startswith("/static")


def is_json_request(request: HttpRequest) -> bool:
    """Определяет, нужно ли вернуть JSON"""
    return request.GET.get("format") == "json" or "application/json" in request.META.get("HTTP_ACCEPT", "")


def _safe_message(exception: Exception | None) -> str | None:
    """
    Текст исключения, если он человекочитаемый. У Resolver404 (обычный 404
    несуществующего URL) в args лежит служебный дамп всего URLConf с путями
    файловой системы — такое наружу не отдаём.
    """
    if exception and exception.args and isinstance(exception.args[0], str):
        return exception.args[0]
    return None


def _handler(request: HttpRequest, exception: Exception, status_code: int) -> HttpResponse:
    error_text = ERROR_TEXTS.get(status_code, "Ошибка")

    if is_media_or_static(request):
        return HttpResponse(status=status_code)

    # В JSON — только сама ошибка. Глобальный контекст сюда класть нельзя:
    # в нём сериализованные пользователи вместе с email-ами
    if is_json_request(request):
        return JsonResponse(
            {
                "error": error_text,
                "message": _safe_message(exception),
                "status_code": status_code,
            },
            status=status_code,
            json_dumps_params={"ensure_ascii": False},
        )

    # Красивая страница требует БД (users), diskcache и чтения тем с диска —
    # всего того, что во время настоящей аварии может быть недоступно.
    # Обработчик ошибки падать не имеет права, поэтому на любой сбой рендера
    # отвечаем простым текстом
    try:
        context = {
            "error": error_text,
            "message": _safe_message(exception),
            "request_path": request.path,
        }
        global_data = GlobalDataMixin()
        context = async_to_sync(global_data.add_context_data)(request, context)
        return render(request, f"errors/{status_code}.html", context, status=status_code)
    except Exception:
        logger.exception("Страница ошибки %s сама не отрендерилась", status_code)
        return HttpResponse(
            f"{status_code} — {error_text}", status=status_code, content_type="text/plain; charset=utf-8"
        )


@requires_csrf_token
def handler400(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    return _handler(request, exception, 400)


@requires_csrf_token
def handler403(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    return _handler(request, exception, 403)


@requires_csrf_token
def handler404(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    return _handler(request, exception, 404)


@requires_csrf_token
def handler500(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    # Django вызывает handler500 без exception — параметр оставлен
    # для единообразия сигнатур
    return _handler(request, exception, 500)


# ======================
# ТЕСТОВЫЕ ВЬЮХИ
# Обработчики ошибок срабатывают только при DEBUG=False, поэтому из браузера
# их иначе не проверить; подключаются в urls.py только в DEBUG-режиме
# ======================


def test_400(request: HttpRequest) -> NoReturn:
    """Генерирует 400 ошибку для тестирования"""
    raise BadRequest("Тестовая 400 ошибка")


def test_403(request: HttpRequest) -> NoReturn:
    """Генерирует 403 ошибку для тестирования"""
    raise PermissionDenied("Тестовая 403 ошибка")


def test_404(request: HttpRequest) -> NoReturn:
    """Генерирует 404 ошибку для тестирования"""
    raise Http404("Тестовая 404 ошибка")


def test_500(request: HttpRequest) -> None:
    """Генерирует 500 ошибку для тестирования"""
    1 / 0  # Это вызовет исключение и приведет к вызову handler500
