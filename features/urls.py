from django.urls import path

from features.views import Catalog, Carousel, MoviesStatistic, Tarots

urlpatterns = [
    path("catalog/", Catalog.as_view(), name='catalog'),
    path("carousel/", Carousel.as_view(), name='carousel'),
    path("statistic/", MoviesStatistic.as_view(), name="statistic"),
    path("tarot/", Tarots.as_view(), name="tarot"),
]
