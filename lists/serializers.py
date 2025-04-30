from rest_framework.serializers import (
    ModelSerializer,
    ListSerializer,
    BaseSerializer,
    ReturnDict,
    DateTimeField,
)
from django.db import models

from lists.models import Movie, Genre, User, Note


class MovieListSerializer(ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.manager.BaseManager) else data

        return {
            self.child.to_representation(item).get(
                "kp_id"
            ): self.child.to_representation(item)
            for item in iterable
        }

    @property
    def data(self):
        ret = BaseSerializer.data.fget(self)
        return ReturnDict(ret, serializer=self)


class MovieSerializer(ModelSerializer):
    premiere = DateTimeField(format="%d/%m/%Y")

    class Meta:
        list_serializer_class = MovieListSerializer
        model = Movie
        fields = [
            "kp_id",
            "name",
            "poster",
            "premiere",
            "description",
            "duration",
            "rating_kp",
            "rating_imdb",
            "is_archive",
        ]


class MovieRatingSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ["kp_id", "rating_imdb", "rating_kp", "poster", "name"]


class MovieSmallSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "kp_id",
            "poster",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        notes = instance.note_set.all()
        representation["notes"] = NoteSerializer(notes, many=True).data
        return representation


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
