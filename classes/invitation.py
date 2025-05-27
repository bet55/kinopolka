import logging
from typing import Dict, List, Optional
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile
from telegram import Bot
from telegram.error import TelegramError
from .postcard import PostcardHandler
from .user import UserHandler
from postcard.models import Postcard
from email.mime.image import MIMEImage

# Configure logger
logger = logging.getLogger('kinopolka')

class Invitation:
    """
    Класс для рассылки открыток на будущие мероприятия
    """

    def __init__(self, postcard: Optional[Postcard] = None, is_active: bool = False):
        """
        Initialize an Invitation instance.

        Args:
            postcard: Optional Postcard instance to associate with the invitation.
            is_active: Boolean indicating if the postcard is active. Defaults to False.
        """
        self.postcard: Optional[Postcard] = postcard
        self.is_active: bool = is_active
        logger.debug("Initialized Invitation with postcard=%s, is_active=%s",
                    postcard.id if postcard else None, is_active)

    @classmethod
    async def create(cls) -> 'Invitation':
        """
        Asynchronously create an Invitation instance by fetching the active postcard.

        Returns:
            An initialized Invitation instance with the active postcard.

        Raises:
            Exception: If fetching the postcard fails, logs the error and initializes with None.
        """
        try:
            postcard, is_active = await PostcardHandler.get_postcard()
            from icecream import ic
            ic(postcard.id, postcard.meeting_date)
            if not postcard:
                logger.warning("No active postcard found for Invitation")
            else:
                logger.info("Fetched active postcard with id=%s for Invitation", postcard.id)
            return cls(postcard, is_active)

        except Exception as e:
            logger.error("Failed to fetch postcard for Invitation: %s", str(e))
            return cls(postcard=None, is_active=False)

    async def send_invitation(self) -> Dict[str, str]:
        """
        Отправляем все приглашения, реализованные в данном классе

        :return: словарь результатов отправки
        """
        if not self.is_active or not self.postcard:
            logger.warning("No active postcard available for invitation")
            return {
                "telegram": "Ошибка: активная открытка не найдена",
                "email": "Ошибка: активная открытка не найдена"
            }

        try:
            screenshot = self.postcard.screenshot
            meeting_date = self.postcard.meeting_date

            if not screenshot or not meeting_date:
                logger.error("Invalid postcard data: screenshot or meeting_date missing")
                return {
                    "telegram": "Ошибка: данные открытки некорректны",
                    "email": "Ошибка: данные открытки некорректны"
                }

            users = await UserHandler.get_all_users()
            emails = [user.get("email") for user in users if user.get("email")]

            if not emails:
                logger.warning("No valid email addresses found for invitation")

            telegram_result = await self.send_telegram(screenshot)
            email_result = self.send_email(screenshot, meeting_date, emails)

            logger.info("Invitation sent: telegram=%s, email=%s", telegram_result, email_result)
            return {"telegram": telegram_result, "email": email_result}

        except Exception as e:
            logger.error("Failed to send invitations: %s", str(e))
            return {
                "telegram": f"Ошибка: {str(e)}",
                "email": f"Ошибка: {str(e)}"
            }

    @classmethod
    def send_email(
        cls,
        screenshot: ImageFieldFile,
        meeting_date: datetime,
        emails: List[str],
    ) -> str:
        """
        Отправляем email с открыткой всем участникам киноклуба

        :param screenshot: картинка открытки
        :param meeting_date: дата и время встречи
        :param emails: список email для отправки
        :return: результат отправки
        """
        if not screenshot or not isinstance(screenshot, ImageFieldFile):
            logger.error("Invalid screenshot provided for email")
            return "Ошибка: некорректная открытка"

        if not isinstance(meeting_date, datetime):
            logger.error("Invalid meeting_date: %s", type(meeting_date))
            return "Ошибка: некорректная дата встречи"

        if not emails or not all(isinstance(email, str) for email in emails):
            logger.warning("No valid emails provided for sending")
            return "Ошибка: список email пуст или содержит некорректные данные"

        try:
            html_content = render_to_string(
                "elements/email.html", {"postcard": screenshot.url, "date": meeting_date}
            )
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject="Ваша персональная открытка",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=emails,
            )
            email.attach_alternative(html_content, "text/html")

            with open(screenshot.path, "rb") as img:
                mime_img = MIMEImage(img.read())
                mime_img.add_header("Content-ID", "<postcard>")
                mime_img.add_header("Content-Disposition", "inline")
                email.attach(mime_img)

            email.send()
            logger.info("Email sent to %d recipients", len(emails))
            return "Открытка была отправлена на email!"

        except FileNotFoundError:
            logger.error("Screenshot file not found: %s", screenshot.path)
            return "Ошибка: файл открытки не найден"
        except Exception as e:
            logger.error("Failed to send email: %s", str(e))
            return f"Ошибка: {str(e)}"

    @classmethod
    async def send_telegram(cls, screenshot: ImageFieldFile) -> str: 
        """
        Отправляем открытку в телеграм группу киноклуба

        :param screenshot: картинка открытки
        :return: результат отправки
        """
        if not screenshot or not isinstance(screenshot, ImageFieldFile):
            logger.error("Invalid screenshot provided for Telegram")
            return "Ошибка: некорректная открытка"

        try:
            bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
            group_id = getattr(settings, "TELEGRAM_GROUP_ID", None)

            if not bot_token or not group_id:
                logger.error("Missing Telegram configuration: bot_token=%s, group_id=%s", bot_token, group_id)
                return "Ошибка: отсутствуют настройки Telegram"

            bot = Bot(token=bot_token)

            with open(screenshot.path, "rb") as img:
                await bot.send_photo(chat_id=group_id, photo=img)

            logger.info("Telegram message sent to group %s", group_id)
            return "Открытка отправлена в телеграм!"

        except FileNotFoundError:
            logger.error("Screenshot file not found: %s", screenshot.path)
            return "Ошибка: файл открытки не найден"
        except TelegramError as e:
            logger.error("Telegram API error: %s", str(e))
            return f"Ошибка: {str(e)}"
        except Exception as e:
            logger.error("Failed to send Telegram message: %s", str(e))
            return f"Ошибка: {str(e)}"