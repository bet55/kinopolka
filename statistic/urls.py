from django.urls import path

from statistic.views import MoviesStatistic

urlpatterns = [
    path("", MoviesStatistic.as_view(), name="statistic_view"),

]
