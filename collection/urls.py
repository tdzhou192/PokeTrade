from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.collection_view, name='collection'),
    path('admin/', admin.site.urls),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('pokemon/<int:pokemon_id>/', views.pokemon_detail_view, name='pokemon_detail'),
    path('trade/<int:marketplace_id>/', views.trade_pokemon_view, name='trade_pokemon'),
    path('populate/', views.populate_collection, name='populate_collection'), 
    path('accounts/', include('django.contrib.auth.urls')),
    path('favorite/<int:pokemon_id>/', views.toggle_favorite, name='toggle_favorite'),
]