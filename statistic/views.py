from rest_framework.decorators import api_view
from django.shortcuts import render
from classes import Statistic, Tools, UserHandler


#  Добавить анимацию пересчета цифр
# https://codepen.io/r-i-c-h/pen/BaXGZXx


@api_view()
def overall_stats(request):
    return render(request, "statistic.html")


@api_view(["GET"])
def movies_stats(request):

    # return render(request, template_name='email.html')
    stat = Statistic.get_movies_statistic()
    fig = Statistic.draw()

    random_images = Tools.get_random_images()
    users = UserHandler.get_all_users()
    top_users_movies = Statistic.most_rated_users_movies()
    top_kp_movies = Statistic.most_rated_kp_movies()

    return render(
        request,
        template_name="statistic.html",
        context={
            "graph_div": fig,
            "statistic": stat,
            "random": random_images,
            "users": users,
            "movies": top_users_movies,
            "kp_movies": top_kp_movies,
        },
    )
