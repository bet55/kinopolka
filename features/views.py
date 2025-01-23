from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from classes import Tools, MovieHandler
from lists.models import AppUser
from lists.serializers import UserSerializer


@api_view(['GET'])
def carousel(request):
    movies = MovieHandler.get_all_movies(all_info=False)

    users = AppUser.objects.all()
    us_sr = UserSerializer(users, many=True)

    random_images = Tools.get_random_images()
    return render(request, 'features/carousel.html',
                  context={'movies': movies,
                           'users': us_sr.data,
                           'random': random_images})
