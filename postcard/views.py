import logging
from adrf.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from classes import Tools, PostcardHandler, Invitation, Error
from mixins import GlobalDataMixin

logger = logging.getLogger('kinopolka')


def handle_response(data, success_status=status.HTTP_200_OK):
    """
    Унифицированная функция для обработки ответов API.
    :param data: Данные ответа (dict, list, bool, или Error).
    :param success_status: HTTP-статус для успешного ответа.
    :return: Response объект.
    """
    if isinstance(data, Error):
        return Response({'error': data.message}, status=data.status)
    return Response(data, status=success_status)


class PostcardsArchiveViewSet(GlobalDataMixin, APIView):
    http_method_names = ['get']

    async def get(self, request: Request):
        """
        Получение страницы архива всех открыток.
        """
        postcards = await PostcardHandler.get_all_postcards()
        if isinstance(postcards, Error):
            logger.error("Failed to retrieve postcards: %s", postcards.message)
            return Response({'error': postcards.message}, status=postcards.status)

        context = await self.add_context_data(request, {"postcards": postcards})
        return render(request, "postcards_archive.html", context=context)


class InvitationViewSet(APIView):
    http_method_names = ['post']

    async def post(self, request: Request):
        """
        Отправка приглашения для следующего мероприятия.
        """
        invitation = await Invitation.create()
        result = await invitation.send_invitation()
        if isinstance(result, dict) and any("Ошибка" in v for v in result.values()):
            logger.error("Failed to send invitation: %s", result)
            return Response({"error": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info("Invitation sent successfully")
        return handle_response(result)


class PostcardViewSet(GlobalDataMixin, APIView):
    http_method_names = ['get', 'post', 'put', 'delete']

    async def get(self, request: Request):
        """
        Получение страницы с текущей активной открыткой.
        """
        theme = request.query_params.get("theme")
        random_images = Tools.get_random_images(theme)
        postcard_data = await PostcardHandler.get_postcard()

        if isinstance(postcard_data, Error):
            logger.error("Failed to retrieve postcard: %s", postcard_data.message)
            postcard_url = random_images.get("postcard")
            is_active = False
        else:
            postcard_url = postcard_data.get('screenshot') or random_images.get("postcard")
            is_active = postcard_data.get('is_active', False)

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
        postcard_data = await PostcardHandler.create_postcard(request.data, request=request)
        return handle_response(postcard_data, status.HTTP_201_CREATED)

    async def put(self, request: Request):
        """
        Деактивация всех открыток.
        """
        success = await PostcardHandler.deactivate_postcard()
        if isinstance(success, Error):
            return handle_response(success)
        return handle_response({"message": "Postcards deactivated"})

    async def delete(self, request: Request):
        """
        Удаление открытки по ID.
        """
        postcard_id = request.data.get("id")

        success = await PostcardHandler.delete_postcard(postcard_id)
        return handle_response(success, status.HTTP_204_NO_CONTENT)