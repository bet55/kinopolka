import pendulum
from django.contrib.auth.models import User as UserModel
from django.db.models import Model
from django.db import models

from lists import validators


def default_countries():
    return ['unknown']

QUESTION_MARK_URL = 'https://banner2.cleanpng.com/20180715/yag/aavjmwzok.webp'


# Create your models here.
class User(UserModel):
    avatar = models.URLField(default=QUESTION_MARK_URL)


class Actor(Model):
    mgr = models.Manager()
    kp_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    photo = models.URLField(default=QUESTION_MARK_URL)


class Director(Model):
    mgr = models.Manager()
    kp_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    photo = models.URLField(default=QUESTION_MARK_URL)


class Writer(Model):
    mgr = models.Manager()
    kp_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    photo = models.URLField(default=QUESTION_MARK_URL)


class MovieGenreRelations(Model):
    movie = models.ForeignKey('lists.Movie', on_delete=models.CASCADE)
    genre = models.ForeignKey('lists.Genre', on_delete=models.CASCADE)


class Genre(Model):
    mgr = models.Manager()
    name = models.CharField(max_length=50, primary_key=True)
    watch_counter = models.IntegerField(default=0)


class Movie(Model):
    # class CustomJSONField(models.JSONField):
    #
    #     def get_prep_value(self, value):
    #         import json
    #         if value is None:
    #             return value
    #         # Почему не работает????????????????????????
    #         return json.dumps(value, ensure_ascii=False)

    mgr = models.Manager()
    kp_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, validators=[validators.validate_name])

    countries = models.JSONField(default=default_countries)
    genres = models.ManyToManyField(Genre)
    # genres = models.ManyToManyField(Genre, through=FilmGenreRelations)
    directors = models.ManyToManyField(Director)
    actors = models.ManyToManyField(Actor)
    writers = models.ManyToManyField(Writer)
    budget = models.IntegerField(default=0)
    fees = models.IntegerField(default=0)
    premiere = models.DateTimeField(default='1900-01-24T09:27:20.807Z')
    description = models.TextField(default='...')
    short_description = models.TextField(default='...')
    slogan = models.TextField(default='...')
    duration = models.IntegerField(default=0)
    poster = models.URLField(default=QUESTION_MARK_URL)
    rating_kp = models.DecimalField(default=0.0, decimal_places=3, max_digits=4)
    rating_imdb = models.DecimalField(default=0.0, decimal_places=3, max_digits=4)
    votes_kp = models.IntegerField(default=0)
    votes_imdb = models.IntegerField(default=0)
    watch_date = models.DateTimeField(null=True)
    is_archive = models.BooleanField(default=False)

    class Meta:
        ordering = ['-rating_kp']


class Note(Model):
    mgr = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField(default='И сказать нечего...')
    rating = models.IntegerField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='user_movie_key'),
        ]
