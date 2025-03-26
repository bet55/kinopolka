from django.urls import path

from postcard.views import view_postcard, PostCardViewSet, send_postcard

urlpatterns = [
    path('', view_postcard),
    path('test_postcard', PostCardViewSet.as_view(), name='test_postcard'),
    path('send_postcard', send_postcard),

]
