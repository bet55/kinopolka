from django.contrib import admin

from lists.models import Actor, Director, Genre, Movie, Note, User, Writer


# Register your models here.
admin.site.register(User)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Writer)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Note)
