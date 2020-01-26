# Web views

from django.urls import path
from . import views

urlpatterns = [
	path('', views.root),
    path('analysis', views.analysis),
    path('snap', views.snap),
	path('nutri', views.nutri),
    path('index', views.index),
<<<<<<< HEAD
=======
    path('nutriInfo', views.nutriInfo),
>>>>>>> d0b6bed738216326a7ea33ffc86d73ed878eed4d
]
