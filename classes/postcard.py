from collections import defaultdict
import logging

from asgiref.sync import sync_to_async
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from lists.models import Movie, Note
from postcard.models import Postcard
from postcard.serializers import PostcardSerializer
from utils.exception_handler import handle_exceptions


logger = logging.getLogger(__name__)


class PostcardHandler:
    @classmethod
    @handle_exceptions("Открытка")
    @sync_to_async
    def create_postcard(cls, data: dict, request=None) -> dict:
        """
        Создание новой открытки. Деактивирует все предыдущие открытки.
        :param data: Словарь с данными открытки (title, meeting_date, screenshot, movies).
        :param request: HTTP-запрос для контекста сериализатора.
        :return: Сериализованные данные открытки или Error.
        """
        if not isinstance(data, dict):
            raise ValidationError("Некорректный тип данных")
        if not data.get("meeting_date"):
            raise ValidationError("Поле 'meeting_date' обязательно")

        cls.deactivate_postcard()  # Деактивируем все открытки

        serializer = PostcardSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")

        postcard = serializer.save()
        return PostcardSerializer(postcard).data

    @classmethod
    @handle_exceptions("Открытка")
    @sync_to_async
    def get_postcard(cls) -> dict:
        """
        Получение активной открытки.
        :return: Сериализованные данные активной открытки или Error.
        """

        postcard = Postcard.objects.filter(is_active=True).latest("created_at")
        return PostcardSerializer(postcard).data

    @classmethod
    @handle_exceptions("Активная открытка")
    @sync_to_async
    def get_postcard_tmp(cls):
        """
        Получение активной открытки.
        :return: Сериализованные данные активной открытки или Error.
        """

        postcard = Postcard.objects.filter(is_active=True).latest("created_at")
        return PostcardSerializer(postcard)

    @classmethod
    @handle_exceptions("Открытка")
    async def get_postcard_by_id(cls, postcard_id: int) -> dict:
        """
        Получение открытки по ID.
        :param postcard_id: ID открытки.
        :return: Сериализованные данные открытки или Error.
        """
        postcard_id = int(postcard_id)
        if postcard_id <= 0:
            raise ValidationError("Некорректный ID открытки")

        postcard = await Postcard.objects.aget(id=postcard_id)
        return PostcardSerializer(postcard).data

    @classmethod
    @handle_exceptions("Открытки")
    @sync_to_async
    def get_all_postcards(cls) -> list[dict]:
        """
        Получение всех открыток.
        :return: Список сериализованных открыток или Error.
        """
        postcards = Postcard.objects.all()
        return PostcardSerializer(postcards, many=True).data

    @classmethod
    @sync_to_async
    def get_all_postcards_with_ratings(cls):
        # Все открытки + подгружаем фильмы с нужными полями
        postcards = Postcard.objects.all().prefetch_related(
            Prefetch(
                'movies',
                queryset=Movie.mgr.only('kp_id', 'name', 'poster_local')
            )
        ).order_by('-meeting_date')

        result = {}

        # Один запрос: все оценки по фильмам из открыток
        notes = Note.mgr.filter(
            movie__postcard__isnull=False
        ).select_related('user', 'movie').values(
            'movie__kp_id',
            'movie__postcard__id',
            'user__id',
            'rating'
        )

        # Группируем оценки: postcard_id → kp_id → {user_id: rating}
        ratings_by_postcard = defaultdict(lambda: defaultdict(dict))
        total_ratings_by_postcard = defaultdict(list)

        for note in notes:
            pc_id = note['movie__postcard__id']
            kp_id = note['movie__kp_id']
            user_id = note['user__id']
            rating = note['rating']

            ratings_by_postcard[pc_id][kp_id][user_id] = rating
            total_ratings_by_postcard[pc_id].append(rating)

        # Формируем результат
        for postcard in postcards:
            pc_id = postcard.id
            movies_list = []

            for movie in postcard.movies.all():
                kp_id = movie.kp_id
                ratings_dict = ratings_by_postcard[pc_id].get(kp_id, {})

                movies_list.append({
                    'kp_id': kp_id,
                    'name': movie.name,
                    'poster_local': movie.poster_local.url if movie.poster_local else "/media/posters/default.png",
                    'ratings': ratings_dict,  # {user_id: rating}
                })

            # Средний рейтинг по всей встрече
            all_ratings = total_ratings_by_postcard[pc_id]
            average_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else '-.-'

            result[pc_id] = {
                'screenshot': postcard.screenshot.url if postcard.screenshot else None,
                'is_active': postcard.is_active,
                'meeting_date': postcard.meeting_date.strftime("%d.%m.%Y %H:%M"),
                'created_at': postcard.created_at.strftime("%d.%m.%Y"),
                'title': postcard.title or f"Встреча {postcard.meeting_date.strftime('%d.%m.%Y')}",
                'average_rating': average_rating,
                'movies': movies_list,  # ← список словарей!
            }
        # ic(result)
        return result

    @classmethod
    @handle_exceptions("Открытка")
    async def update_postcard(cls, data: dict, request=None) -> dict:
        """
        Обновление открытки.
        :param data: Словарь с данными для обновления (должен содержать 'id').
        :param request: HTTP-запрос для контекста сериализатора.
        :return: Сериализованные данные обновленной открытки или Error.
        """
        if not isinstance(data, dict) or "id" not in data:
            raise ValidationError("Некорректные данные или отсутствует ID")

        postcard = await Postcard.objects.aget(id=data["id"])
        serializer = PostcardSerializer(postcard, data=data, partial=True, context={"request": request})
        if not await sync_to_async(serializer.is_valid)():
            raise ValidationError(f"Невалидные данные: {serializer.errors}")
        updated_postcard = await sync_to_async(serializer.save)()
        return PostcardSerializer(updated_postcard).data

    @classmethod
    @handle_exceptions("Открытка")
    async def delete_postcard(cls, postcard_id: int) -> bool:
        """
        Удаление открытки по ID.
        :param postcard_id: ID открытки.
        :return: True если удаление успешно, иначе Error.
        """
        postcard_id = int(postcard_id)
        if postcard_id <= 0:
            raise ValidationError("Некорректный ID открытки")

        postcard = await Postcard.objects.aget(id=postcard_id)
        await postcard.adelete()
        return True

    @classmethod
    @handle_exceptions("Открытки")
    @sync_to_async
    def deactivate_postcard(cls, postcard_id: int = None, update_all: bool = True) -> bool:
        """
        Деактивация одной или всех открыток.
        :param postcard_id: ID открытки для деактивации (опционально).
        :param update_all: Если True, деактивировать все открытки.
        :return: True если деактивация успешна, иначе Error.
        """
        if update_all:
            Postcard.objects.all().update(is_active=False)
            return True
        if not isinstance(postcard_id, int) or postcard_id <= 0:
            raise ValidationError("Некорректный ID открытки")
        postcard = Postcard.objects.get(id=postcard_id)
        postcard.is_active = False
        postcard.save()
        return True
