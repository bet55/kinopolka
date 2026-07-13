# Тесты TeaCodeMiddleware — границы доступа «свой-чужой».
# Middleware тестируется в изоляции (RequestFactory + фиктивный get_response),
# чтобы не зависеть от view, БД и внешних API.
import json

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from utils.middleware import TEA_CODE_COOKIE_MAX_AGE, TEA_CODE_KEY, UNSAFE_METHODS, TeaCodeMiddleware


CODE = "secret-tea"


def _ok_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


async def _ok_response_async(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


@override_settings(TEA_CODE=CODE, SSL_REDIRECT=False)
class TeaCodeAccessTests(SimpleTestCase):
    """Кто проходит, кто получает 403."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.middleware = TeaCodeMiddleware(_ok_response)

    def test_get_without_code_passes(self) -> None:
        # Просмотр открыт всем — сайт можно показывать посторонним
        response = self.middleware(self.factory.get("/lists/movies/"))
        self.assertEqual(response.status_code, 200)

    def test_unsafe_methods_without_code_denied(self) -> None:
        for method in UNSAFE_METHODS:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/lists/movies/")
                response = self.middleware(request)
                self.assertEqual(response.status_code, 403)

    def test_denied_response_is_json_with_error(self) -> None:
        response = self.middleware(self.factory.post("/lists/movies/"))
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", json.loads(response.content))

    def test_post_with_valid_code_in_query_passes(self) -> None:
        response = self.middleware(self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}={CODE}"))
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_code_in_cookie_passes(self) -> None:
        request = self.factory.post("/lists/movies/")
        request.COOKIES[TEA_CODE_KEY] = CODE
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_post_with_wrong_code_denied(self) -> None:
        request = self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}=wrong")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_wrong_code_in_cookie_but_valid_in_query_passes(self) -> None:
        # GET-параметр приоритетнее куки: свежая ссылка должна работать
        # даже с протухшей кукой от старого кода
        request = self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}={CODE}")
        request.COOKIES[TEA_CODE_KEY] = "stale-old-code"
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_boss_admin_is_exempt(self) -> None:
        # У админки своя авторизация — middleware не вмешивается
        response = self.middleware(self.factory.post("/boss/lists/movie/add/"))
        self.assertEqual(response.status_code, 200)

    @override_settings(TEA_CODE="")
    def test_empty_tea_code_disables_protection(self) -> None:
        response = self.middleware(self.factory.post("/lists/movies/"))
        self.assertEqual(response.status_code, 200)

    @override_settings(TEA_CODE="чайный-код")
    def test_non_ascii_code_works(self) -> None:
        # compare_digest со строками не-ASCII кидает TypeError, поэтому в
        # middleware сравниваются bytes — проверяем, что кириллица не роняет
        request = self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}=чайный-код")
        self.assertEqual(self.middleware(request).status_code, 200)
        wrong = self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}=неверный")
        self.assertEqual(self.middleware(wrong).status_code, 403)


@override_settings(TEA_CODE=CODE, SSL_REDIRECT=False)
class TeaCodeCookieTests(SimpleTestCase):
    """Запоминание кода в куке: вход по ссылке ?tea_code=XXX."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.middleware = TeaCodeMiddleware(_ok_response)

    def test_valid_code_in_query_sets_cookie(self) -> None:
        response = self.middleware(self.factory.get(f"/?{TEA_CODE_KEY}={CODE}"))
        cookie = response.cookies[TEA_CODE_KEY]
        self.assertEqual(cookie.value, CODE)
        self.assertEqual(cookie["max-age"], TEA_CODE_COOKIE_MAX_AGE)
        self.assertTrue(cookie["httponly"])  # JS про код не знает
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertFalse(cookie["secure"])

    @override_settings(SSL_REDIRECT=True)
    def test_cookie_is_secure_on_prod(self) -> None:
        response = self.middleware(self.factory.get(f"/?{TEA_CODE_KEY}={CODE}"))
        self.assertTrue(response.cookies[TEA_CODE_KEY]["secure"])

    def test_wrong_code_does_not_set_cookie(self) -> None:
        response = self.middleware(self.factory.get(f"/?{TEA_CODE_KEY}=wrong"))
        self.assertNotIn(TEA_CODE_KEY, response.cookies)

    def test_no_code_does_not_set_cookie(self) -> None:
        response = self.middleware(self.factory.get("/"))
        self.assertNotIn(TEA_CODE_KEY, response.cookies)

    def test_cookie_not_reset_if_already_present(self) -> None:
        # Кука уже стоит — не переставляем, чтобы не сбрасывать её срок жизни
        request = self.factory.get(f"/?{TEA_CODE_KEY}={CODE}")
        request.COOKIES[TEA_CODE_KEY] = CODE
        response = self.middleware(request)
        self.assertNotIn(TEA_CODE_KEY, response.cookies)

    @override_settings(TEA_CODE="")
    def test_empty_tea_code_does_not_set_cookie(self) -> None:
        response = self.middleware(self.factory.get(f"/?{TEA_CODE_KEY}=anything"))
        self.assertNotIn(TEA_CODE_KEY, response.cookies)


@override_settings(TEA_CODE=CODE, SSL_REDIRECT=False)
class TeaCodeAsyncTests(SimpleTestCase):
    """Приложение работает на ASGI (uvicorn) — проверяем асинхронную ветку."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.middleware = TeaCodeMiddleware(_ok_response_async)

    def test_async_mode_detected(self) -> None:
        self.assertTrue(self.middleware.async_mode)

    async def test_post_without_code_denied(self) -> None:
        response = await self.middleware(self.factory.post("/lists/movies/"))
        self.assertEqual(response.status_code, 403)

    async def test_post_with_valid_code_passes_and_sets_cookie(self) -> None:
        response = await self.middleware(self.factory.post(f"/lists/movies/?{TEA_CODE_KEY}={CODE}"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies[TEA_CODE_KEY].value, CODE)

    async def test_get_without_code_passes(self) -> None:
        response = await self.middleware(self.factory.get("/lists/movies/"))
        self.assertEqual(response.status_code, 200)
