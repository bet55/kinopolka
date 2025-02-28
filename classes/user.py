from lists.models import User
from lists.serializers import UserSerializer


class UserHandler:
    """
    Класс для работы с пользователями в базе данных
    """
    @classmethod
    def get_user(self, user_id: int | str) -> dict:
        app_user = User.objects.get(pk=user_id)
        serialized_user = UserSerializer(app_user)
        return serialized_user.data

    @classmethod
    def get_all_users(self) -> list:
        all_app_users = User.objects.all()
        serialized_all_app_users = UserSerializer(all_app_users, many=True)
        return serialized_all_app_users.data
