from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.collection_view, name='collection'),
]