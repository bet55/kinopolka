from django.shortcuts import render
from adrf.decorators import api_view
from django.shortcuts import render
from rest_framework.request import Request
from classes import Tools, MovieHandler, UserHandler, PostcardHandler
from lists.models import User
from lists.serializers import UserSerializer


@api_view(["GET"])
async def carousel(request: Request):
    movies = await MovieHandler.get_all_movies(info_type="posters")
    users = await UserHandler.get_all_users()

    random_images = Tools.get_random_images()
    return render(
        request,
        "features/carousel.html",
        context={"movies": movies, "users": users, "random": random_images},
    )


@api_view(['GET'])
async def postcards_archive(request: Request):
    postcards = await PostcardHandler.get_all_postcards()
    users = await UserHandler.get_all_users()


    random_images = Tools.get_random_images()
    return render(
        request,
        "features/postcards_archive.html",
        context={"postcards": postcards,  "users": users, "random": random_images},
    )
