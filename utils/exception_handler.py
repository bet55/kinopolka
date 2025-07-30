from functools import wraps
from typing import Callable
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from classes.exceptions import ErrorHandler
import logging

logger = logging.getLogger(__name__)


def handle_exceptions(resource_name: str) -> Callable:
    """
    Декоратор для перехвата ошибок и перевода их в формат, возвращаемы пользователю
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Ошибка валидации в {resource_name}: {str(e)}")
                status_code = getattr(e, 'status_code', 400)
                error = ErrorHandler(str(e), status=status_code)
                return error.to_dict()
            except ObjectDoesNotExist as e:
                logger.error(f"Объект не найден в {resource_name}: {str(e)}")
                return ErrorHandler("Запрашиваемый объект не найден", status=404).to_dict()
            except Exception as e:
                logger.error(f"Ошибка в {resource_name}: {str(e)}", exc_info=True)
                error = ErrorHandler(f"{str(e)}", status=500)
                return error.to_dict()
        return async_wrapper
    return decorator