from django.urls import path, include
from testc import views


urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.test, name='video_feed'),
    ]
