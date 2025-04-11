from django.db import models
import pendulum
from lists.models import Movie


class Postcard(models.Model):
    meeting_date = models.DateTimeField()
    title = models.CharField(max_length=255, null=True)
    movies = models.ManyToManyField(Movie)
    created_at = models.DateTimeField(
        default=pendulum.now("Asia/Yekaterinburg").to_date_string()
    )
    is_active = models.BooleanField(default=True)
    screenshot = models.ImageField(upload_to="media/postcards/", null=True)
