from django.db import models
import pendulum
from lists.models import Movie


class Postcard(models.Model):
    meeting_date = models.DateTimeField()
    movies = models.ManyToManyField(Movie)
    created_at = models.DateTimeField(default=pendulum.now('Asia/Yekaterinburg').to_date_string())
    #TODO: think about 1 active card at a time
    #is_active = models.BooleanField(default=True)
