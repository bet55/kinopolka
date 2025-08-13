"""
URL configuration for filmoclub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .view import (
    handler400,
    handler403,
    handler404,
    handler500,
)


# Обрабатываем ошибки всего проекта
handler400 = handler400
handler403 = handler403
handler404 = handler404
handler500 = handler500

# Пробуем в документацию приложения
schema_view = get_schema_view(
    openapi.Info(
        title="Filmoclub API",
        default_version="v0.7.0",
        description="API for managing postcards, invitations, and other features in the Filmoclub project.",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)

urlpatterns = [
    # path('test/400/', test_400),
    # path('test/403/', test_403),
    # path('test/404/', test_404),
    # path('test/500/', test_500),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("movies/", include("lists.urls")),
    path("", include("postcard.urls")),
    path("tools/", include("tools.urls")),
    path("features/", include("features.urls")),
    path("bar/", include("bar.urls")),
    # API Documentation Endpoints
    path("api/schema/", schema_view.without_ui(cache_timeout=0), name="schema"),
    path(
        "api/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="redoc",
    ),
]

# Когда-то пришлось добавить, чтобы локально грузилась статика. Работает только в дебаг моде
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
