# Web views

from django.urls import path
from . import views

urlpatterns = [
	path('', views.root),
    path('analysis', views.analysis),
    path('snap', views.snap),
	path('nutri', views.nutri),
    path('index', views.index),
    path('get_nutrition', views.get_nutrition)
]
