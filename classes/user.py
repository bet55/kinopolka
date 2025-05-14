import logging
from typing import Dict, List, Optional
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from lists.models import User
from lists.serializers import UserSerializer
from asgiref.sync import sync_to_async

# Configure logger
logger = logging.getLogger('kinopolka')

class UserHandler:
    """
    Класс для работы с пользователями в базе данных
    """

    @classmethod
    async def get_user(cls, user_id: int | str) -> Optional[Dict]:
        """
        Retrieve a user by their ID.

        :param user_id: Id нужного пользователя.

        :return: Информация о пользователе или None в случаи ошибки.
        """
        if not user_id or not isinstance(user_id, (int, str)) or (isinstance(user_id, int) and user_id <= 0):
            logger.error("Invalid user_id: %s", user_id)
            return None

        try:
            app_user = await User.objects.aget(pk=user_id)
            serialized_user = UserSerializer(app_user)
            logger.info("Retrieved user with id: %s", user_id)
            return serialized_user.data

        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            logger.warning("Failed to retrieve user %s: %s", user_id, str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error retrieving user %s: %s", user_id, str(e))
            return None

    @classmethod
    @sync_to_async
    def get_all_users(cls) -> List[Dict]:
        """
        Получение всех пользователей.

        :return: Информация о пользователях или пустой список.
        """
        try:
            all_app_users = User.objects.all()
            serialized_all_app_users = UserSerializer(all_app_users, many=True)
            logger.info("Retrieved %d users", all_app_users.count())
            return serialized_all_app_users.data

        except Exception as e:
            logger.error("Failed to retrieve all users: %s", str(e))
            return []