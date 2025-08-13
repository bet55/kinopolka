import logging

from rest_framework import status as drf_status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from classes.exceptions import ErrorHandler


logger = logging.getLogger(__name__)


def handle_response(data: dict, success_data: dict | None = None, status: drf_status = HTTP_200_OK) -> Response:
    """
    Унифицированная функция для обработки ответов API.
    :param data: Данные для валидации ответа
    :param success_data: Возвращаемые данные при успешном сценарии
    :param status: HTTP-статус для успешного ответа.
    :return: Response объект.
    """

    if isinstance(data, dict) and data.get("error"):
        data = ErrorHandler(message=data["error"]["message"], status=data["error"]["status"])

    if isinstance(data, ErrorHandler):
        return Response({"error": data.message}, status=data.status)

    success_data = success_data if success_data else data
    return Response(success_data, status=status)
