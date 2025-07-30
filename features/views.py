from adrf.views import APIView
from django.shortcuts import render
from rest_framework.request import Request
from classes import Statistic, MovieHandler
from mixins import GlobalDataMixin
from utils.response_handler import handle_response


class Catalog(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        return render(
            request,
            template_name="features/catalog.html",
            context=await self.add_context_data(request, {}),
        )


class MoviesStatistic(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        # fig = await Statistic.draw()

        statistic = await Statistic.get_movies_statistic()
        top_imdb_movies = await Statistic.most_rated_imdb_movies()
        top_users_movies = await Statistic.most_rated_users_movies()

        context = {
            # "graph_div": fig,
            "statistic": statistic,
            "movies": top_users_movies,
            "imdb_movies": top_imdb_movies,
        }

        return render(
            request,
            template_name="features/statistic.html",
            context=await self.add_context_data(request, context),
        )


class Carousel(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        movies = await MovieHandler.get_all_movies(info_type="posters")

        return render(
            request,
            "features/carousel.html",
            context=await self.add_context_data(request, {"movies": movies}),
        )


class Tarots(GlobalDataMixin, APIView):
    async def get(self, request: Request):
        return render(
            request,
            "features/tarot.html",
            context=await self.add_context_data(request, {}),
        )
