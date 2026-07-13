# Тесты обработчиков ошибок проекта (filmoclub/view.py).
# В тестах DEBUG всегда False, поэтому кастомные обработчики активны
# и для запросов через test client.
import json
from unittest.mock import patch

from django.http import Http404
from django.test import Client, RequestFactory, TestCase

from filmoclub.view import handler404, handler500


class ErrorHandlersUnitTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_json_response_contains_only_error_fields(self) -> None:
        # Глобальный контекст (users с email-ами и т.п.) наружу утекать не должен
        request = self.factory.get("/nope/", HTTP_ACCEPT="application/json")
        response = handler404(request, Http404("нет такого"))
        self.assertEqual(response.status_code, 404)
        payload = json.loads(response.content)
        self.assertEqual(set(payload.keys()), {"error", "message", "status_code"})
        self.assertEqual(payload["error"], "Страница не найдена")

    def test_resolver_404_details_are_hidden(self) -> None:
        # Resolver404 несёт в args дамп URLConf с путями файловой системы —
        # в ответе его быть не должно
        request = self.factory.get("/nope/", HTTP_ACCEPT="application/json")
        response = handler404(request, Http404({"tried": ["<весь URLConf>"], "path": "nope/"}))
        self.assertIsNone(json.loads(response.content)["message"])

    def test_error_text_matches_status(self) -> None:
        request = self.factory.get("/nope/", HTTP_ACCEPT="application/json")
        response = handler500(request)
        self.assertEqual(json.loads(response.content)["error"], "Ошибка сервера")

    def test_static_path_returns_empty_response_with_status(self) -> None:
        request = self.factory.get("/static/nope.css")
        response = handler404(request, Http404())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"")

    def test_render_failure_falls_back_to_plain_text(self) -> None:
        # Обработчик ошибки не имеет права падать: если красивая страница
        # не собралась (БД, кэш, битый шаблон) — отдаём простой текст
        request = self.factory.get("/nope/")
        with patch("filmoclub.view.render", side_effect=Exception("всё сломалось")):
            response = handler500(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Ошибка сервера", response.content.decode())


class ErrorHandlersIntegrationTests(TestCase):
    """Через полный стек: URL → обработчик → шаблон errors/*.html."""

    def test_unknown_url_renders_404_page(self) -> None:
        response = self.client.get("/definitely/not/a/page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_unhandled_exception_renders_500_page(self) -> None:
        client = Client(raise_request_exception=False)
        response = client.get("/test/500/")
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "errors/500.html")
