import logging
from dataclasses import dataclass
from typing import ClassVar, Optional, Dict, Any, Union
import httpx
from django.conf import settings
from classes.caching import Caching

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class KP:
    """
    Класс для работы с неофициальным api кинопоиска https://kinopoisk.dev
    """

    CACHE_DIRECTORY: str = 'app_cache'
    CACHE_DURATION: int = 60 * 2  # 2 minutes
    cache: Caching = Caching(CACHE_DIRECTORY, CACHE_DURATION)

    error: Optional[str] = None
    BASE_URL: ClassVar[str] = "https://api.kinopoisk.dev/v1.4/"
    headers: ClassVar[Dict[str, str]] = None  # Initialized in __post_init__

    def __post_init__(self):
        """Initialize headers with API key from settings."""
        try:
            self.headers = {"X-API-KEY": settings.KP_API_TOKEN}
        except AttributeError:
            logger.error("KP_API_TOKEN not found in Django settings")
            self.headers = {}
            self.error = "Missing KP_API_TOKEN in settings"

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Make an HTTP request to the Kinopoisk API with caching.

        Args:
            url: API endpoint URL (relative to BASE_URL).
            params: Optional query parameters for the request.

        Returns:
            Response data as a dictionary if successful, None if an error occurs.
        """
        if not url or not isinstance(url, str):
            logger.error("Invalid URL: %s", url)
            self.error = "Invalid URL provided"
            return None

        if params and not isinstance(params, dict):
            logger.error("Invalid params type: %s", type(params))
            self.error = "Invalid params type"
            return None

        if not self.headers.get("X-API-KEY"):
            logger.error("Cannot make request: Missing API key")
            self.error = "Missing API key"
            return None

        # Generate cache key
        cache_key = f"{self.BASE_URL}{url}" + (str(params) if params else "")
        cached_value = self.cache.get_cache(cache_key)
        if cached_value:
            logger.info("Retrieved cached data for %s", cache_key)
            return cached_value

        try:
            with httpx.Client(base_url=self.BASE_URL, headers=self.headers) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                response_data = response.json()
                self.cache.set_cache(cache_key, response_data)
                logger.info("Successfully fetched data from %s", url)
                return response_data

        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error for %s: %s", url, str(e))
            self.error = f"HTTP error: {str(e)}"
            return None
        except httpx.RequestError as e:
            logger.error("Network error for %s: %s", url, str(e))
            self.error = f"Network error: {str(e)}"
            return None
        except ValueError as e:
            logger.error("Invalid JSON response for %s: %s", url, str(e))
            self.error = f"Invalid JSON response: {str(e)}"
            return None
        except Exception as e:
            logger.error("Unexpected error for %s: %s", url, str(e))
            self.error = f"Unexpected error: {str(e)}"
            return None


@dataclass
class KP_Movie(KP):
    """
    Класс для получения фильмов кинопоиска
    """

    BASE_URL: ClassVar[str] = KP.BASE_URL + "movie"

    def get_movie_by_id(self, movie_id: Union[str, int]) -> Optional[Dict]:
        """
        Получение информации о фильме.

        :param movie_id: Id кинопоиска нужного фильма.

        :return: Словарь с информацией о фильме или None в случаи ошибки.
        """
        if not movie_id or not isinstance(movie_id, (str, int)) or (isinstance(movie_id, int) and movie_id <= 0):
            logger.error("Invalid movie_id: %s", movie_id)
            self.error = "Invalid movie_id provided"
            return None

        return self._make_request(str(movie_id))
