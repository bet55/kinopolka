import logging

from asgiref.sync import sync_to_async
from rest_framework.exceptions import ValidationError

from lists.models import User
from lists.serializers import UserSerializer
from utils.exception_handler import handle_exceptions


# Configure logger
logger = logging.getLogger(__name__)


class UserHandler:
    """
    Класс для работы с пользователями в базе данных.
    """

    @classmethod
    @handle_exceptions("Пользователь")
    async def get_user(cls, user_id: int | str) -> dict:
        """
        Получение пользователя по ID.
        :param user_id: ID пользователя (целое число или строка).
        :return: Сериализованные данные пользователя.
        """
        if not user_id or not isinstance(user_id, (int, str)) or (isinstance(user_id, int) and user_id <= 0):
            raise ValidationError("Некорректный user_id")

        app_user = await User.objects.aget(pk=user_id)
        return UserSerializer(app_user).data

    @classmethod
    @handle_exceptions("Пользователи")
    @sync_to_async
    def get_all_users(cls) -> list[dict]:
        """
        Получение всех пользователей.
        :return: Список сериализованных пользователей.
        """
        all_app_users = User.objects.all()
        logger.info("Получено %d пользователей", all_app_users.count())
        return UserSerializer(all_app_users, many=True).data
