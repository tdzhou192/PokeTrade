from django.urls import path
from . import views

urlpatterns = [
    path('collection/', views.collection_view, name='collection'),
    path('favorite/<int:pokemon_id>/', views.toggle_favorite, name='toggle_favorite'),
]