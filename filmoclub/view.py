from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.urls import Resolver404
from django.views.decorators.csrf import requires_csrf_token


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


@requires_csrf_token
def handler400(request, exception=None):
    if is_media_or_static(request):
        return HttpResponseNotFound()

    context = {
        "error": "Неверный запрос",
        "message": str(exception) if exception else None,
    }
    if is_json_request(request):
        return JsonResponse({**context, "status_code": 400}, status=400)
    return render(request, "errors/400.html", context, status=400)


@requires_csrf_token
def handler403(request, exception=None):
    if is_media_or_static(request):
        return HttpResponseNotFound()

    context = {
        "error": "Доступ запрещён",
        "message": str(exception) if exception else None,
    }
    if is_json_request(request):
        return JsonResponse({**context, "status_code": 403}, status=403)
    return render(request, "errors/403.html", context, status=403)


@requires_csrf_token
def handler404(request, exception: Resolver404 = None):
    if is_media_or_static(request):
        return HttpResponseNotFound()

    context = {
        "error": "Страница не найдена",
        "message": "увы",
        "request_path": request.path,
    }
    if is_json_request(request):
        return JsonResponse({**context, "status_code": 404}, status=404)
    return render(request, "errors/404.html", context, status=404)


@requires_csrf_token
def handler500(request):
    if is_media_or_static(request):
        return HttpResponseNotFound()

    context = {"error": "Ошибка сервера"}
    if is_json_request(request):
        return JsonResponse({**context, "status_code": 500}, status=500)
    return render(request, "errors/500.html", context, status=500)


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
