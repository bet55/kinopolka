from rest_framework.exceptions import APIException


class MoviesError(APIException):
    status_code = 500
    default_detail = "movies broke"
    default_code = "error"


class TooManyActivePostcardsError(Exception):
    default_detail = "Too many active postcards"
    default_code = "error"
    status_code = 500


class ErrorHandler:
    """
    Класс, который служит для создания читаемого представления на основе ошибок.
    Каждая функция, которая может выбрасывать исключение оборачивается в handle_exceptions.
    handle_exceptions создаёт экземпляр ErrorHandler, который уже можно обработать и вернуть в качестве
    ответа пользователю

    :param message: str описание ошибки
    :param status: int статус код

    """
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status

    def to_dict(self):
        return {
            "error": {
                "message": self.message,
                "status": self.status
            }
        }

    def __dict__(self):
        return self.to_dict()

    def __str__(self):
        return self.message
