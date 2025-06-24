import logging
from functools import wraps
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError
from .error import Error
from bar.models import Ingredient, Cocktail


logger = logging.getLogger('kinopolka')


def handle_exceptions(method_name: str):
    """Обёртка над классами коктейлей и """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (Ingredient.DoesNotExist, Cocktail.DoesNotExist):
                logger.error(f"{method_name} не найден: {args}, {kwargs}")
                return Error(message=f"{method_name} не найден", status=404)
            except ValidationError as e:
                logger.error(f"Ошибка валидации в {method_name}: {str(e)}")
                return Error(message=str(e), status=400)
            except Exception as e:
                logger.error(f"Ошибка в {method_name}: {str(e)}")
                return Error(message=f"Ошибка в {method_name}: {str(e)}")
        return wrapper
    return decorator


def custom_exception_handler(exception, context):
    """Общий перехватчик для всего django"""
    response = exception_handler(exception, context)

    match exception.__class__:
        case MoviesError:
            pass  # we can do smth here

    return response
