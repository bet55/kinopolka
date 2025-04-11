from django.contrib import admin

from lists.models import User, Actor, Director, Writer, Genre, Movie, Note

# Register your models here.
admin.site.register(User)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Writer)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Note)
