from rest_framework.exceptions import APIException


class MoviesError(APIException):
    status_code = 500
    default_detail = "movies broke"
    default_code = "error"


class TooManyActivePostcardsError(Exception):
    default_detail = "Too many active postcards"
    default_code = "error"
    status_code = 500
