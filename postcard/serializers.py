from asgiref.sync import sync_to_async
from rest_framework import serializers

from lists.serializers import MovieDictSerializer
from postcard.models import Postcard

# class PostcardSerializer(serializers.ModelSerializer):
#     movies = MovieDictSerializer(many=True)
#     created_at = serializers.DateTimeField(format="%d.%m.%Y", read_only=True)
#     meeting_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M")
#
#     class Meta:
#         model = Postcard
#         fields = ["id", "meeting_date", "movies", "is_active", "screenshot", "title", "created_at"]
#
#     async def create(self, validated_data):
#         """
#         Асинхронное создание открытки.
#         :param validated_data: Валидированные данные.
#         :return: Созданная открытка.
#         """
#         movies = validated_data.pop('movies', [])
#         postcard = await sync_to_async(lambda: Postcard(
#             title=validated_data.get('title'),
#             meeting_date=validated_data["meeting_date"],
#             screenshot=validated_data.get("screenshot"),
#         ))()
#         await sync_to_async(postcard.save)()
#         if movies:
#             await sync_to_async(lambda: postcard.movies.set(movies))()
#         return postcard
#
#     async def update(self, instance, validated_data):
#         """
#         Асинхронное обновление открытки.
#         :param instance: Экземпляр открытки.
#         :param validated_data: Валидированные данные.
#         :return: Обновленная открытка.
#         """
#         movies = validated_data.pop('movies', [])
#         instance.meeting_date = validated_data.get("meeting_date", instance.meeting_date)
#         instance.title = validated_data.get("title", instance.title)
#         instance.screenshot = validated_data.get("screenshot", instance.screenshot)
#         await sync_to_async(instance.save)()
#         if movies:
#             await sync_to_async(lambda: instance.movies.set(movies))()
#         return instance


class PostcardSerializer(serializers.ModelSerializer):
    movies = MovieDictSerializer
    created_at = serializers.DateTimeField(format="%d.%m.%Y", read_only=True)
    meeting_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M")

    class Meta:
        model = Postcard
        fields = [
            "id",
            "meeting_date",
            "movies",
            "is_active",
            "screenshot",
            "title",
            "created_at",
        ]

    def create(self, validated_data):
        postcard = Postcard(
            title=validated_data["title"],
            meeting_date=validated_data["meeting_date"],
            screenshot=validated_data["screenshot"],
        )
        postcard.save()
        postcard.movies.set(validated_data["movies"])
        return postcard

    def update(self, instance, validated_data):
        instance.meeting_date = validated_data["meeting_date"]
        instance.save()
        instance.movies.set(validated_data["movies"])
        return instance
