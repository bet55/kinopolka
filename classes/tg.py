from functools import wraps
import logging

from django.conf import settings
from telegram import Bot

from utils import ErrorHandler


logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Перехватываем ошибки"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"Файл для отправки не найден: {e!s}")
            return ErrorHandler(message=str(e), status=404)
        except Exception as e:
            logger.error(f"Ошибка отправки telegram сообщения : {e!s}")
            return ErrorHandler(message=f"Ошибка отправки telegram сообщения : {e!s}")

    return wrapper


class Telegram:
    def __init__(self):
        self.is_init = False
        self._create_bot_instance()

    def _create_bot_instance(self):
        self.bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        self.group_id = getattr(settings, "TELEGRAM_GROUP_ID", None)

        if not self.bot_token or not self.group_id:
            logger.error("Missing Telegram configuration")
            return ErrorHandler(message="Ошибка: отсутствуют настройки Telegram")

        self.bot = Bot(token=self.bot_token)
        self.is_init = True
        return True

    @handle_exceptions
    async def send_image(self, file_path: str):
        with open(file_path, "rb") as img:
            await self.bot.send_photo(chat_id=self.group_id, photo=img)

        logger.info(
            "Telegram image sent to group",
        )
        return "Открытка отправлена в телеграм!"

    @handle_exceptions
    async def send_message(self, message: str) -> str:
        await self.bot.send_message(chat_id=self.group_id, text=message, parse_mode="HTML")

        logger.info(
            "Telegram message sent to group",
        )
        return "Открытка отправлена в телеграм!"
