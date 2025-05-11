from django.urls import path

from features.views import carousel, postcards_archive

urlpatterns = [
    path("carousel/", carousel),
    path("postcards_archive/", postcards_archive),
]
