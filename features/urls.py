from django.urls import path

from features.views import CarouselView, PostcardsView

urlpatterns = [
    path("carousel/", CarouselView.as_view(), name='carousel'),
    path("postcards_archive/", PostcardsView.as_view(), name='postcards_archive'),
]
