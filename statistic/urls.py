from django.urls import path

from statistic.views import movies_stats

urlpatterns = [path("", movies_stats)]
