from rest_framework.serializers import (
    ModelSerializer,
    ListSerializer,
    BaseSerializer,
    ReturnDict,
    DateTimeField,
)
from django.db import models

from lists.models import Movie, Genre, User, Note


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


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


class MovieDictSerializer(ModelSerializer):
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

        representation['genres'] = [genre['name'] for genre in representation['genres']]
        poster_local = instance.poster_local.url if instance.poster_local else '/media/posters/default.png'
        representation['poster_local'] = instance.poster if 'default' in poster_local else poster_local
        return representation


class MovieRatingSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ["kp_id", "rating_imdb", "rating_kp", "poster", "poster_local", "name"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        poster_local = instance.poster_local.url if instance.poster_local else '/media/posters/default.png'
        representation['poster_local'] = instance.poster if 'default' in poster_local else poster_local
        return representation


class MoviePosterSerializer(ModelSerializer):
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
        representation["notes"] = NoteSerializer(notes, many=True).data
        representation['genres'] = [genre['name'] for genre in representation['genres']]
        poster_local = instance.poster_local.url if instance.poster_local else '/media/posters/default.png'
        representation['poster_local'] = instance.poster if 'default' in poster_local else poster_local
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
        ]


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
