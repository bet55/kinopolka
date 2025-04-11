from adrf.decorators import api_view
from adrf.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from classes import Tools, UserHandler, PostcardHandler, Invitation

import logging
logger = logging.getLogger('kinopolka_logger')

@api_view(['GET'])
def tmp(request: Request):
    logger.info('I am here')
    return Response({'res': 'nice'})


class InvitationViewSet(APIView):
    def post(self, request: Request):
        """
        Делаем рассылку о следующем чаепитие
        """
        invitation = Invitation()
        result = invitation.send_invitation()
        return Response(result)


class PostCardViewSet(APIView):
    def get(self, request: Request):
        """
        Получаем страницу с открыткой текущего мероприятия
        """
        users = UserHandler.get_all_users()
        random_images = Tools.get_random_images()
        postcard, is_active = PostcardHandler.get_postcard()

        postcard = (
            postcard.screenshot.url if is_active else random_images.get("postcard")
        )

        context = {
            "postcard": postcard,
            "random": random_images,
            "users": users,
            "is_active": is_active,
        }
        return render(request, "postcard.html", context=context)

    def post(self, request: Request):
        """
        Создаём новую открытку
        """
        postcard, success = PostcardHandler.create_postcard(request.data)
        if success:
            return Response(data=postcard, status=status.HTTP_201_CREATED)
        return Response(data=postcard, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request):
        """
        Делаем все открытки неактивными
        """
        PostcardHandler.deactivate_postcard()
        return Response(data={"Postcards deactivated"}, status=status.HTTP_201_CREATED)

    def delete(self, request: Request):
        """
        Удаляем выбранную открытку
        """
        result = PostcardHandler.delete_postcard(request.data["id"])
        if result:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
