# Web views

from django.urls import path
from . import views

urlpatterns = [
	path('', views.root),
    path('analysis', views.analysis),
    path('snap', views.snap),
	path('nutri', views.nutri),
    #path('index', views.index),
    #path('nutriInfo', views.nutriInfo),
]
handler404 = 'web.views.handler404'
handler500 = 'web.views.handler500'
