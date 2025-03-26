from django.core.mail import EmailMessage

from adrf.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from classes import Tools
from classes.postcard import PostcardHandler
from lists.models import User
from lists.serializers import UserSerializer
from django.core.mail import send_mail


@api_view(['GET'])
def view_postcard(request):
    users = User.objects.all()
    us_sr = UserSerializer(users, many=True)
    random_images = Tools.get_random_images()
    return render(request, 'postcard.html', context={'random': random_images, 'users': us_sr.data})


@api_view(['GET'])
def send_postcard(request):
    active_postcard = PostcardHandler.get_active_postcard()
    screenshot = active_postcard.background_picture
    subject = 'Киноклуб уже скоро!'
    body = 'Приглашаем вас на очередное заседание киноклуба!'
    email = EmailMessage(
        subject,
        body,
        '9261881@gmail.com',
        [
                  '9261881@gmail.com',
                  'stepanda96@yandex.ru'
        ],
    )
    with screenshot.open("rb") as image_file:
        email.attach(
            filename=screenshot.name,
            content=image_file.read(),
            mimetype="image/jpg"
        )
    email.send()
    return Response(status=status.HTTP_200_OK)


class PostCardViewSet(APIView):
    def get(self, request):
        postcard = PostcardHandler.get_postcard(request.data['id'])
        if postcard:
            return Response(data=postcard, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        postcard, success = PostcardHandler.create_postcard(request.data)
        if success:
            return Response(data=postcard, status=status.HTTP_201_CREATED)
        return Response(data=postcard, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        updated_postcard, success = PostcardHandler.update_postcard(request.data)
        if success:
            return Response(data=updated_postcard, status=status.HTTP_200_OK)
        if updated_postcard:
            return Response(data=updated_postcard, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        result = PostcardHandler.delete_postcard(request.data['id'])
        if result:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
