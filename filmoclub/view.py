from asgiref.sync import async_to_sync
from django.core.exceptions import BadRequest, PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.urls import Resolver404
from django.views.decorators.csrf import requires_csrf_token

from mixins import GlobalDataMixin


# ======================
# ОБРАБОТЧИКИ ОШИБОК
# requires_csrf_token не используется, но оставим на будущее
# ======================


def is_media_or_static(request):
    """Проверяет, запрашивается ли статика или медиа"""
    path = request.path
    return path.startswith("/media") or path.startswith("/static")


def is_json_request(request):
    """Определяет, нужно ли вернуть JSON"""
    return request.GET.get("format") == "json" or "application/json" in request.META.get("HTTP_ACCEPT", "")


def _handler(request: WSGIRequest, exception, status_code):
    if is_media_or_static(request):
        return HttpResponseNotFound()

    context = {
        "error": "Неверный запрос",
        "message": str(exception) if exception else None,
        "request_path": request.path,
    }
    global_data = GlobalDataMixin()
    context = async_to_sync(global_data.add_context_data)(request, context)

    if is_json_request(request):
        return JsonResponse({**context, "status_code": status_code}, status=status_code)
    return render(request, f"errors/{status_code}.html", context, status=status_code)


@requires_csrf_token
def handler400(request, exception=None):
    return _handler(request, exception, 400)


@requires_csrf_token
def handler403(request, exception=None):
    return _handler(request, exception, 403)


@requires_csrf_token
def handler404(request, exception: Resolver404 = None):
    return _handler(request, exception, 404)


@requires_csrf_token
def handler500(request, exception=None):
    return _handler(request, exception, 500)


# ======================
# ТЕСТОВЫЕ ВЬЮХИ
# ======================


def test_400(request):
    """Генерирует 400 ошибку для тестирования"""
    raise BadRequest("Тестовая 400 ошибка")


def test_403(request):
    """Генерирует 403 ошибку для тестирования"""
    raise PermissionDenied("Тестовая 403 ошибка")


def test_404(request):
    """Генерирует 404 ошибку для тестирования"""
    raise Http404("Тестовая 404 ошибка")


def test_500(request):
    """Генерирует 500 ошибку для тестирования"""
    1 / 0  # Это вызовет исключение и приведет к вызову handler500
