# Web views

from django.urls import path
from . import views

urlpatterns = [
	path('', views.root),
    path('feed', views.feed),
    path('analysis', views.analysis),
    path('temp', views.theme_index),
	path('nutri', views.nutri),
]
