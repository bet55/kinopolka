from rest_framework.serializers import ModelSerializer, SerializerMethodField

from features.models import Photo
from lists.models import Movie


DEFAULT_POSTER = "/media/posters/default.png"


class PhotoSerializer(ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "name", "description", "image", "uploaded_at"]


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

    def get_poster_local(self, obj: Movie) -> str:
        return obj.poster_local.url if obj.poster_local else DEFAULT_POSTER
