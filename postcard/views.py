from adrf.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from classes import Tools, UserHandler, PostcardHandler


class PostCardViewSet(APIView):
    def get(self, request: Request):
        users = UserHandler.get_all_users()
        random_images = Tools.get_random_images()
        postcard, is_active = PostcardHandler.get_postcard()

        postcard = postcard.background_picture.url if is_active else random_images.get('postcard')

        print(postcard, is_active)

        context = {
            'postcard': postcard,
            'random': random_images,
            'users': users,
            'is_active': is_active
        }
        return render(request, 'postcard.html', context=context)

    def post(self, request: Request):
        postcard, success = PostcardHandler.create_postcard(request.data)
        if success:
            return Response(data=postcard, status=status.HTTP_201_CREATED)
        return Response(data=postcard, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request):
        PostcardHandler.deactivate_postcard()
        return Response(data={'Postcards deactivated'}, status=status.HTTP_201_CREATED)

    def delete(self, request: Request):
        result = PostcardHandler.delete_postcard(request.data['id'])
        if result:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
