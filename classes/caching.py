import logging
from sqlite3 import OperationalError
from typing import Any, Union
from diskcache import Cache

# Configure logger
logger = logging.getLogger('kinopolka')


class Caching:
    """
    Класс для кэширования данных
    """

    def __init__(self, dirname: str = None, ttl: int = None):
        """
        :param dirname: (str) - название папки хранения файла кэша.
        :param ttl: (int) время актуальности кэша в секундах.
        """
        # Признак успешности инициализации
        self.__initialized: bool = True

        # Сообщение об ошибке
        self.__error_message: str = ""

        # Проверка параметров
        if dirname and type(dirname) is not str:
            self.__error_message = "Переданный dirname не является строкой."
            logger.error(self.__error_message)
            self.__initialized = False
            return None
        if ttl and type(ttl) is not int:
            self.__error_message = "Переданный ttl не является целым числом."
            logger.error(self.__error_message)
            self.__initialized = False
            return None
        if ttl and ttl < 0:
            self.__error_message = "Переданн отрицательный ttl."
            logger.error(self.__error_message)
            self.__initialized = False
            return None

        self.__dirname = dirname if dirname else None
        self.__ttl = ttl if ttl else None

        # Инициализация кэшировальщика
        self.__cache = None
        try:
            self.__cache = Cache(self.__dirname)
        except OperationalError as e:
            self.__error_message = (
                f"При инициализации кэшировальщика возникла ошибка. [{str(e)}]"
            )
            logger.error(self.__error_message)
            self.__initialized = False
            return None
        except Exception as e:
            self.__error_message = f"При инициализации кэшировальщика возникла непредвиденная ошибка. [{str(e)}]"
            logger.error(self.__error_message)
            self.__initialized = False
            return None

    def check_cache(self, key: Union[str, int] = None) -> bool:
        """
        Проверка наличия параметра в кэше.
        :param key: (int|str) параметр в кэше.
        :return: (bool) результат проверки.
        """
        # Проверка параметров
        if key is None:
            return False
        if type(key) not in [int, str]:
            self.__error_message = (
                "Переданный key не является целым числом или строкой."
            )
            logger.error(self.__error_message)
            return False

        return key in self.__cache

    def get_cache(self, key: Union[str, int] = None) -> Any:
        """
        Получение данных из кэша.
        :param key: (int|str) ключ размещения данных в кэше.
        :return: (any) python-объект данных из кэша.
        """
        # Проверка параметров
        if key is None:
            self.__error_message = "Параметр key не задан."
            logger.error(self.__error_message)
            return None
        if key and type(key) not in [int, str]:
            self.__error_message = (
                "Переданный key не является целым числом или строкой."
            )
            logger.error(self.__error_message)
            return None

        # Получение данных из кэша
        try:
            return self.__cache.get(key)
        except TypeError:
            self.__error_message = "Не удалось получить данные из кэша."
            logger.error(self.__error_message)
            return False
        except Exception:
            self.__error_message = (
                "При получении данных из кэша возникла непредвиденная ошибка."
            )
            logger.error(self.__error_message)
            return False

    def get_error_message(self) -> str:
        return self.__error_message

    def get_status(self) -> bool:
        return self.__initialized

    def set_cache(self, key: Union[str, int] = None, value: Any = None) -> bool:
        """
        Размещение данных в кэш.
        :param key: (int|str) ключ размещения данных в кэше.
        :param value: (any) python-объект.
        :return: (bool) результат кэширования.
        """
        # Проверка параметров
        if key is None:
            self.__error_message = "Параметр key не задан."
            logger.error(self.__error_message)
            return False
        if key and type(key) not in [int, str]:
            self.__error_message = (
                "Переданный key не является целым числом или строкой."
            )
            logger.error(self.__error_message)
            return False

        # Кэширование данных
        try:
            return self.__cache.set(key, value, expire=self.__ttl)
        except TypeError:
            self.__error_message = "Не удалось закэшировать данные."
            logger.error(self.__error_message)
            return False
        except Exception:
            self.__error_message = (
                "При кэшировании данных возникла непредвиденная ошибка."
            )
            logger.error(self.__error_message)
            return False
