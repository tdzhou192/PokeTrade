from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('', views.collection_view, name='collection'),
    path('admin/', admin.site.urls),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('pokemon/<int:pokemon_id>/', views.pokemon_detail_view, name='pokemon_detail'),
    path('trade/<int:marketplace_id>/', views.trade_pokemon_view, name='trade_pokemon'),
    path('purchase/<int:pokemon_id>/', views.purchase_pokemon_view, name='purchase_pokemon'),
    path('owned/<int:pokemon_id>/', views.owned_pokemon_detail_view, name='owned_pokemon_detail'),
    path('populate/', views.populate_collection, name='populate_collection'),
    path('favorite/<int:pokemon_id>/', views.toggle_favorite, name='toggle_favorite'),
    # New URLs for listed Pokemon operations:
    path('listed/<int:pokemon_id>/', views.listed_pokemon_detail_view, name='listed_pokemon_detail'),
    path('purchase_listed/<int:pokemon_id>/', views.purchase_listed_pokemon_view, name='purchase_listed_pokemon'),
    path('trade_listed/<int:pokemon_id>/', views.trade_for_listed_pokemon_view, name='trade_for_listed_pokemon'),
    path('list/<int:pokemon_id>/', views.list_pokemon_for_sale_view, name='list_pokemon_for_sale'),
]