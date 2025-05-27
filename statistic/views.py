from adrf.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from classes import Statistic, Tools, UserHandler, NoteHandler
from mixins import GlobalDataMixin

#  Добавить анимацию пересчета цифр
# https://codepen.io/r-i-c-h/pen/BaXGZXx


@api_view()
def overall_stats(request):
    return render(request, "statistic.html")


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
            template_name="statistic.html",
            context=await self.add_context_data(request, context),
        )
