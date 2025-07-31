import logging

from adrf.views import APIView
from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from classes import Invitation, PostcardHandler, Tools
from mixins import GlobalDataMixin
from utils.response_handler import handle_response

logger = logging.getLogger(__name__)


class PostcardsArchiveViewSet(GlobalDataMixin, APIView):
    http_method_names = ["get"]

    async def get(self, request: Request):
        """
        Получение страницы архива всех открыток.
        """
        postcards = await PostcardHandler.get_all_postcards()

        response_format = request.query_params.get("format")
        if response_format == "json":
            return Response(postcards, status=status.HTTP_200_OK)

        context = await self.add_context_data(request, {"postcards": postcards})
        return render(request, "postcards_archive.html", context=context)


class InvitationViewSet(APIView):
    http_method_names = ["post"]

    async def post(self, request: Request):
        """
        Отправка приглашения для следующего мероприятия.
        """
        invitation = await Invitation.create()
        result = await invitation.send_invitation()
        return handle_response(result)


class PostcardViewSet(GlobalDataMixin, APIView):
    http_method_names = ["get", "post", "put", "delete"]

    async def get(self, request: Request):
        """
        Получение страницы с текущей активной открыткой.
        Если активной открытки нет отображаем шаблон для заполнения.
        """
        theme = request.query_params.get("theme")
        random_images = Tools.get_random_images(theme)

        postcard_url = random_images.get("postcard")
        is_active = False

        postcard_data = await PostcardHandler.get_postcard()

        if not postcard_data.get("error"):
            postcard_url = postcard_data.get("screenshot") or random_images.get(
                "postcard"
            )
            is_active = postcard_data.get("is_active", False)

        context = {
            "postcard": postcard_url,
            "random": random_images,
            "is_active": is_active,
        }
        context = await self.add_context_data(request, context)
        return render(request, "postcard.html", context=context)

    async def post(self, request: Request):
        """
        Создание новой открытки.
        """
        postcard_data = await PostcardHandler.create_postcard(
            request.data, request=request
        )
        return handle_response(postcard_data, status=status.HTTP_201_CREATED)

    async def put(self, request: Request):
        """
        Деактивация всех открыток.
        """
        result = await PostcardHandler.deactivate_postcard()
        return handle_response(result, {"message": "Postcards deactivated"})

    async def delete(self, request: Request):
        """
        Удаление открытки по ID.
        """
        postcard_id = request.data.get("id")

        result = await PostcardHandler.delete_postcard(postcard_id)
        return handle_response(result, status=status.HTTP_204_NO_CONTENT)
