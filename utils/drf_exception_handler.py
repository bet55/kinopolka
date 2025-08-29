import logging

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def drf_exception_handler(exc, context):
    response = exception_handler(exc, context)

    custom_response_data = {
        "error": True,
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "Internal server error",
        "exception": str(exc),
    }

    if isinstance(exc, ValidationError):
        custom_response_data.update(
            {
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid input data",
                "errors": response.data if response else str(exc),
            }
        )
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, PermissionDenied):
        custom_response_data.update(
            {
                "code": status.HTTP_403_FORBIDDEN,
                "message": "Permission denied",
            }
        )
        return Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)

    elif isinstance(exc, NotFound):
        custom_response_data.update(
            {
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Resource not found",
            }
        )
        return Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)

    elif response is not None:
        # Для всех остальных обработанных DRF ошибок
        custom_response_data.update(
            {
                "code": response.status_code,
                "message": response.data.get("detail", "An error occurred"),
            }
        )
        return Response(custom_response_data, status=response.status_code)

    # Для необработанных исключений
    logger.error(f"Unhandled exception: {exc!s} in {context['view']}")
    return Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
