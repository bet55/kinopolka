from adrf.views import APIView
from django.shortcuts import render
from rest_framework.request import Request
from classes import MovieHandler, PostcardHandler
from mixins import GlobalDataMixin

class CarouselView(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        movies = await MovieHandler.get_all_movies(info_type="posters")

        return render(
            request,
            "features/carousel.html",
            context = await self.add_context_data(request, {"movies": movies}),
        )


class PostcardsView(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        postcards = await PostcardHandler.get_all_postcards()

        return render(
            request,
            "features/postcards_archive.html",
            context = await self.add_context_data(request, {"postcards": postcards}),
        )
