from django.db import models
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from lists.models import Genre, Movie, Actor, Director, Writer

DEFAULT_POSTER = "/media/posters/default.png"

class BaseMovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ["kp_id", "name", "poster"]

class BaseRelatedSerializer(ModelSerializer):
    movies = SerializerMethodField()
    movies_count = SerializerMethodField()

    # Define the ManyToMany relationship field name (to be overridden by subclasses)
    related_field = "movie_set"  # Default to reverse relation

    class Meta:
        abstract = True
        fields = ["name", "movies", "movies_count"]  # Base fields, extended by subclasses

    def get_movies(self, obj):
        related_manager = getattr(obj, self.related_field)
        return list(related_manager.all().values_list("kp_id", flat=True))

    def get_movies_count(self, obj):
        related_manager = getattr(obj, self.related_field)
        return related_manager.all().count()

class ActorSerializer(BaseRelatedSerializer):
    class Meta(BaseRelatedSerializer.Meta):
        model = Actor
        fields = BaseRelatedSerializer.Meta.fields + ["kp_id", "photo"]

class DirectorSerializer(BaseRelatedSerializer):
    class Meta(BaseRelatedSerializer.Meta):
        model = Director
        fields = BaseRelatedSerializer.Meta.fields + ["kp_id", "photo"]

class WriterSerializer(BaseRelatedSerializer):
    class Meta(BaseRelatedSerializer.Meta):
        model = Writer
        fields = BaseRelatedSerializer.Meta.fields + ["kp_id", "photo"]

class GenreSerializer(BaseRelatedSerializer):
    class Meta(BaseRelatedSerializer.Meta):
        model = Genre
        fields = BaseRelatedSerializer.Meta.fields + ["watch_counter"]

class MovieRatingSerializer(ModelSerializer):
    poster_local = SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "kp_id",
            "name",
            "rating_imdb",
            "rating_kp",
            "votes_kp",
            "votes_imdb",
            "poster_local",
            "duration",
            "budget",
            "fees",
            "premiere",
        ]

    def get_poster_local(self, obj):
        return obj.poster_local.url if obj.poster_local else DEFAULT_POSTER