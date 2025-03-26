from django.urls import path

from postcard.views import PostCardViewSet, send_email

urlpatterns = [
    path('', PostCardViewSet.as_view(), name='postcard_views'),
    path('email/', send_email, name='postcard_views'),

]
