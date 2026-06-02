from django.urls import path

from features.views import (
    Casino,
    Roulette,
    Cards,
    Slots,
    EightBall,
    Catalog,
    Gym,
    MoviesStatistic,
    Tarots,
)


urlpatterns = [
    path("catalog/", Catalog.as_view(), name="catalog"),
    path("casino/", Casino.as_view(), name="casino"),
    path("casino/roulette/", Roulette.as_view(), name="roulette"),
    path("casino/cards/", Cards.as_view(), name="cards"),
    path("casino/slots/", Slots.as_view(), name="slots"),
    path("casino/8ball/", EightBall.as_view(), name="8ball"),
    path("statistic/", MoviesStatistic.as_view(), name="statistic"),
    path("tarot/", Tarots.as_view(), name="tarot"),
    path("gym/", Gym.as_view(), name="gym"),
]
