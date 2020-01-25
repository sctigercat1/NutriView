# Web views

from django.urls import path
from . import views

urlpatterns = [
	path('', views.root),
    path('feed', views.feed),
    path('analysis', views.analysis),
    path('snap', views.snap),
	path('nutri', views.nutri),
]
