from rest_framework import serializers

from lists.serializers import MovieDictSerializer
from postcard.models import Postcard


class PostcardSerializer(serializers.ModelSerializer):
    movies = MovieDictSerializer
    created_at = serializers.DateTimeField(format="%d.%m.%Y", read_only=True)
    meeting_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M")

    class Meta:
        model = Postcard
        fields = ["id", "meeting_date", "movies", "is_active", "screenshot", "title", "created_at"]

    def create(self, validated_data):
        postcard = Postcard(
            title=validated_data['title'],
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
