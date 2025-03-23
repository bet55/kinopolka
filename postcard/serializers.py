from rest_framework import serializers

from lists.serializers import MovieSerializer
from postcard.models import Postcard


class PostcardSerializer(serializers.ModelSerializer):
    movies = MovieSerializer

    class Meta:
        model = Postcard
        fields = ['meeting_date',
                  'movies',
                  'is_active',
                  'background_picture',
                  ]

    def create(self, validated_data):
        postcard = Postcard(
            meeting_date=validated_data['meeting_date'],
            background_picture=validated_data['background_picture'],
        )
        postcard.save()
        postcard.movies.set(validated_data['movies'])
        return postcard

    def update(self, instance, validated_data):
        instance.meeting_date = validated_data['meeting_date']
        instance.save()
        instance.movies.set(validated_data['movies'])
        return instance
