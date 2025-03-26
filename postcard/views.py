from adrf.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from classes import Tools, UserHandler, PostcardHandler
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@api_view(['POST'])
def send_email(request: Request):
    users = UserHandler.get_all_users()
    emails = [user.get('email') for user in users]

    postcard, is_active = PostcardHandler.get_postcard()
    date = postcard.meeting_date

    html_content = render_to_string('email.html', {
        'postcard': postcard.screenshot.url, 'date': date
    })

    text_content = strip_tags(html_content)  # Текстовая версия

    # Создание письма
    email = EmailMultiAlternatives(
        subject="Ваша персональная открытка",
        body=text_content,
        from_email=None,  # Использует DEFAULT_FROM_EMAIL
        to=emails,
    )
    email.attach_alternative(html_content, "text/html")

    # Прикрепляем изображение (если нужно вложение)
    # email.attach_file(postcard.background_picture.path)

    # Добавляем изображение как inline-вложение
    if postcard.screenshot:
        with open(postcard.screenshot.path, 'rb') as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', '<postcard>')
            mime_img.add_header('Content-Disposition', 'inline')
            email.attach(mime_img)

    email.send()

    return Response(data={'Email отправлен'}, status=status.HTTP_200_OK)


class PostCardViewSet(APIView):
    def get(self, request: Request):
        users = UserHandler.get_all_users()
        random_images = Tools.get_random_images()
        postcard, is_active = PostcardHandler.get_postcard()

        postcard = postcard.screenshot.url if is_active else random_images.get('postcard')

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
