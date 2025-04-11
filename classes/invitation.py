from .postcard import PostcardHandler
from .user import UserHandler
from postcard.models import Postcard

from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from telegram import Bot

from django.db.models.fields.files import ImageFieldFile
from django.db.models.fields import EmailField
from datetime import datetime


class Invitation:
    """
    Класс для рассылки открыток на будущие мероприятия
    """

    def __init__(self):
        postcard, is_active = PostcardHandler.get_postcard()
        self.postcard: Postcard = postcard
        self.is_active: bool = is_active

    async def send_invitation(self) -> dict[str, str]:
        """
        Отправляем все приглашения, реализованные в данном классе

        :return: словарь результатов отправки
        """
        screenshot = self.postcard.screenshot
        meeting_date = self.postcard.meeting_date

        users = UserHandler.get_all_users()
        emails = [user.get("email") for user in users]

        telegram_result = await self.send_telegram(screenshot)
        email_result = self.send_email(screenshot, meeting_date, emails)

        return {"telegram": telegram_result, "email": email_result}

    @classmethod
    def send_email(
        cls,
        screenshot: ImageFieldFile,
        meeting_date: datetime,
        emails: list[EmailField],
    ) -> str:
        """
        Отправляем email с открыткой всем участникам киноклуба

        :param screenshot: картинка открытки
        :param meeting_date: дата и время встречи
        :param emails: список email для отправки
        :return: результат отправки
        """

        html_content = render_to_string(
            "email.html", {"postcard": screenshot.url, "date": meeting_date}
        )

        text_content = strip_tags(html_content)  # Текстовая версия

        try:

            # Создание письма
            email = EmailMultiAlternatives(
                subject="Ваша персональная открытка",
                body=text_content,
                from_email=None,  # Использует DEFAULT_FROM_EMAIL
                to=emails,
            )
            email.attach_alternative(html_content, "text/html")

            # Добавляем изображение как inline-вложение
            with open(screenshot.path, "rb") as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header("Content-ID", "<postcard>")
                mime_img.add_header("Content-Disposition", "inline")
                email.attach(mime_img)


            email.send()
        except Exception as e:
            return str(e)

        return "Открытка была отправлена на email!"

    @classmethod
    async def send_telegram(cls, screenshot: ImageFieldFile) -> str:
        """
        Отправляем открытку в телеграм группу киноклуба

        :param screenshot: картинка открытки
        :return: результат отправки
        """
        TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
        TELEGRAM_GROUP_ID = settings.TELEGRAM_GROUP_ID

        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)

            with open(screenshot.path, "rb") as img:
                await bot.send_photo(chat_id=TELEGRAM_GROUP_ID, photo=img)

            return "Открытка отправлена в телеграм!"

        except Exception as e:
            return str(e)
