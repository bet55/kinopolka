from adrf.views import APIView
from django.shortcuts import render
from rest_framework.request import Request

from classes import MovieHandler, Statistic
from mixins import GlobalDataMixin


class Catalog(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            template_name="features/catalog.html",
            context=await self.add_context_data(request, {}),
        )


class MoviesStatistic(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        statistic = Statistic()
        await statistic.extract_data()

        common_stats = await statistic.statistic()
        movies = await statistic.outstanding_movies()
        genres = await statistic.outstanding_genres()
        graphs = await statistic.draw()

        context = {
            "statistic": common_stats,
            "movies_rating": movies,
            "genres_table": genres,
            "graphs": graphs,
        }

        return render(
            request,
            template_name="features/statistic.html",
            context=await self.add_context_data(request, context),
        )


class Casino(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/casino.html",
            context=await self.add_context_data(request, {}),
        )


class Roulette(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        movies = await MovieHandler.get_all_movies(info_type="posters")

        return render(
            request,
            "features/casino/roulette.html",
            context=await self.add_context_data(request, {"movies": movies}),
        )


class Cards(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/casino/cards.html",
            context=await self.add_context_data(request, {}),
        )


class Slots(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/casino/slots.html",
            context=await self.add_context_data(request, {}),
        )


class EightBall(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/casino/8ball.html",
            context=await self.add_context_data(request, {}),
        )


class Tarots(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/tarot.html",
            context=await self.add_context_data(request, {}),
        )


class Gym(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        return render(
            request,
            "features/gym.html",
            context=await self.add_context_data(request, {}),
        )
