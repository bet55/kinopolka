from django.db import models
from rest_framework.serializers import (
    BaseSerializer,
    DateTimeField,
    ListSerializer,
    ModelSerializer,
    ReturnDict,
)

from features.serializers import GenreSerializer
from lists.models import Movie, Note, User


DEFAULT_POSTER = "/media/posters/default.png"

class NoteSerializer(ModelSerializer):
    """
    Сериализатор для оценок пользователей
    """
    class Meta:
        model = Note
        fields = "__all__"



class MovieListSerializer(ListSerializer):
    """
    Класс для изменения типа возвращаемых сериализатором данных: из list в dict
    """

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.manager.BaseManager) else data

        return {
            self.child.to_representation(item).get("kp_id"): self.child.to_representation(item) for item in iterable
        }

    @property
    def data(self):
        ret = BaseSerializer.data.fget(self)
        return ReturnDict(ret, serializer=self)


class MovieDictSerializer(ModelSerializer):
    """
    Сериализатор для детальной обработки фильмов. Обычно на клиенте.
    {kp_id: {kp_id: 1, name: "boss nigger" ...}}
    """

    premiere = DateTimeField(format="%d/%m/%Y")
    genres = GenreSerializer(many=True)

    class Meta:
        list_serializer_class = MovieListSerializer
        model = Movie
        fields = [
            "kp_id",
            "name",
            "poster",
            "poster_local",
            "premiere",
            "description",
            "duration",
            "rating_kp",
            "rating_imdb",
            "genres",
            "is_archive",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["genres"] = [genre["name"] for genre in representation["genres"]]
        poster_local = instance.poster_local.url if instance.poster_local else "/media/posters/default.png"
        representation["poster_local"] = instance.poster if "default" in poster_local else poster_local
        return representation


class MoviePosterSerializer(ModelSerializer):
    """
    Сериализтаор для отрисовки постеров в html.
    Поэтому многие поля не нужны.
    Жанры добавлены для сортировки.
    """

    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = [
            "kp_id",
            "poster",
            "poster_local",
            "genres",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        notes = instance.note_set.all()
        poster_local = instance.poster_local
        representation["poster_local"] = poster_local.url if poster_local else DEFAULT_POSTER
        representation["notes"] = NoteSerializer(notes, many=True).data
        representation["genres"] = [genre["name"] for genre in representation["genres"]]

        return representation




class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar"
        ]
