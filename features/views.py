from pathlib import Path
import random

from adrf.views import APIView
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from classes import MovieHandler, PhotoHandler, Statistic
from mixins import GlobalDataMixin
from utils.response_handler import handle_response


class Catalog(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            template_name="features/catalog.html",
            context=await self.add_context_data(request, {}),
        )


class MoviesStatistic(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        statistic = Statistic()
        await statistic.extract_data()

        common_stats = await statistic.statistic()
        movies = await statistic.outstanding_movies()
        genres = await statistic.outstanding_genres()
        graphs = await statistic.draw()
        persons = await statistic.outstanding_persons()
        users_stat = await statistic.users_statistic()
        records = await statistic.records()
        compatibility = await statistic.taste_compatibility()
        disputes = await statistic.controversial_movies()

        context = {
            "statistic": common_stats,
            "movies_rating": movies,
            "genres_table": genres,
            "graphs": graphs,
            "persons": persons,
            "users_statistic": users_stat,
            "records": records,
            "compatibility": compatibility,
            "disputes": disputes,
        }

        return render(
            request,
            template_name="features/statistic.html",
            context=await self.add_context_data(request, context),
        )


class Tournament(GlobalDataMixin, APIView):
    """
    Турнир TMNT: эмулятор NES с легальным дампом игры. Четыре бота дерутся
    по турнирной сетке, каждый участник ставит на бойца и вешает на него
    свой фильм из закладок (клиентская корзина в localStorage, поэтому
    селекты фильмов заполняет tournament.js) — чей боец победил, тот фильм
    и смотрим. ROM и save-state'ы лежат в media/roms/ (вне git, синкается с VPS).
    """

    http_method_names = ["get"]

    ROM_PATH = Path("media/roms/tmnt-tournament.nes")
    STATES_DIR = Path("media/roms")

    async def get(self, request: Request) -> HttpResponse:
        # Стейты — заготовленные расстановки бойцов; каждый раз грузим случайную
        states = sorted(self.STATES_DIR.glob("*.state"))
        state_url = f"/{random.choice(states)}" if states else ""

        context = {
            "rom_url": f"/{self.ROM_PATH}" if self.ROM_PATH.exists() else "",
            "state_url": state_url,
        }

        return render(
            request,
            "features/casino/tournament.html",
            context=await self.add_context_data(request, context),
        )


class Casino(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/casino.html",
            context=await self.add_context_data(request, {}),
        )


class Roulette(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        movies = await MovieHandler.get_all_movies(info_type="posters")

        return render(
            request,
            "features/casino/roulette.html",
            context=await self.add_context_data(request, {"movies": movies}),
        )


class Cards(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/casino/cards.html",
            context=await self.add_context_data(request, {}),
        )


class Slots(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/casino/slots.html",
            context=await self.add_context_data(request, {}),
        )


class EightBall(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/casino/8ball.html",
            context=await self.add_context_data(request, {}),
        )


class Tarots(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/tarot.html",
            context=await self.add_context_data(request, {}),
        )


class Photos(GlobalDataMixin, APIView):
    http_method_names = ["get", "post"]

    async def get(self, request: Request) -> HttpResponse:
        """
        Страница с фотографиями клуба
        """
        photos = await PhotoHandler.get_all_photos()

        return render(
            request,
            "features/photos.html",
            context=await self.add_context_data(request, {"photos": photos}),
        )

    async def post(self, request: Request) -> Response:
        """
        Загрузка новой фотографии (multipart: image, name, description)
        """
        photo = await PhotoHandler.create_photo(request.data)
        return handle_response(photo, status=status.HTTP_201_CREATED)


class PhotoDetail(APIView):
    http_method_names = ["patch", "delete"]

    async def patch(self, request: Request, pk: int) -> Response:
        """
        Обновление названия/описания фотографии
        """
        photo = await PhotoHandler.update_photo(pk, request.data)
        return handle_response(photo)

    async def delete(self, request: Request, pk: int) -> Response:
        """
        Удаление фотографии
        """
        response_id = await PhotoHandler.delete_photo(pk)
        return handle_response(response_id, status=status.HTTP_204_NO_CONTENT)


class Gym(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request) -> HttpResponse:
        return render(
            request,
            "features/gym.html",
            context=await self.add_context_data(request, {}),
        )
