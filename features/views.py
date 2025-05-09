from django.shortcuts import render
from adrf.decorators import api_view

from classes import Tools, MovieHandler, UserHandler
from lists.models import User
from lists.serializers import UserSerializer


@api_view(["GET"])
async def carousel(request):
    movies = await MovieHandler.get_all_movies(info_type="posters")
    users = await UserHandler.get_all_users()

    random_images = Tools.get_random_images()
    return render(
        request,
        "features/carousel.html",
        context={"movies": movies, "users": users, "random": random_images},
    )
