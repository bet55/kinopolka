from rest_framework.views import exception_handler


def custom_exception_handler(exception, context):
    response = exception_handler(exception, context)

    match exception.__class__:
        case MoviesError:
            pass  # we can do smth here

    return response
