from django.contrib.auth.models import User

from lists.models import AppUser
from lists.serializers import UserSerializer


class AppUserHandler:
    @classmethod
    def get_user(self, user_id: int | str) -> dict:
        app_user = AppUser.objects.get(pk=user_id)
        serialized_user = UserSerializer(app_user)
        return serialized_user.data

    @classmethod
    def get_all_users(self) -> list:
        all_app_users = AppUser.objects.all()
        serialized_all_app_users = UserSerializer(all_app_users, many=True)
        return serialized_all_app_users.data
