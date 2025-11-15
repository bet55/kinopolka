import logging
from typing import Any

from rest_framework.request import Request

from classes import Caching, Tools, UserHandler


logger = logging.getLogger("kinopolka")


class GlobalDataMixin:
    """Миксин для добавления users и random_images (с theme) в тело ответа."""

    # Настройки кэширования (в секундах)
    CACHE_DIRECTORY: str = "app_cache"
    CACHE_USERS_KEY: str = "global_users"
    CACHE_USERS_TIMEOUT: int = 60 * 15
    cache: Caching = Caching(CACHE_DIRECTORY, CACHE_USERS_TIMEOUT)

    async def get_global_data(self, request: Request, context: dict[str, Any]) -> dict[str, Any]:
        """Возвращает кэшированные или свежие данные."""
        response = {}
        try:
            query_params = getattr(request, "query_params", dict())
            theme = query_params.get("theme")

            if "users" not in context:
                response["users"] = await self._get_cached_users()

            if "random" not in context:
                response["random"] = Tools.get_random_images(theme)

            if "theme" not in context:
                response["theme"] = theme

            return response

        except Exception as e:
            logger.error(f"Failed to fetch global data: {e}")
            return response

    async def _get_cached_users(self) -> list:
        """Возвращает кэшированных пользователей или запрашивает свежих."""
        cached_users = self.cache.get_cache(self.CACHE_USERS_KEY)
        if cached_users:
            return cached_users

        users = await UserHandler.get_all_users()
        self.cache.set_cache(self.CACHE_USERS_KEY, users)
        return users

    async def add_context_data(self, request: Request, context: dict[str, Any]) -> dict[str, Any]:
        """Для TemplateResponse."""
        context.update(await self.get_global_data(request, context))
        return context
