from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('', views.collection_view, name='collection'),
    path('admin/', admin.site.urls),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('trade/<int:marketplace_id>/', views.trade_pokemon_view, name='trade_pokemon'),
    path('purchase/<int:pokemon_id>/', views.purchase_pokemon_view, name='purchase_pokemon'),
    path('owned/<int:pokemon_id>/', views.owned_pokemon_detail_view, name='owned_pokemon_detail'),
    path('populate/', views.populate_collection, name='populate_collection'),
    path('favorite/<int:pokemon_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('listed/<int:pokemon_id>/', views.listed_pokemon_detail_view, name='listed_pokemon_detail'),
    path('purchase_listed/<int:pokemon_id>/', views.purchase_listed_pokemon_view, name='purchase_listed_pokemon'),
    path('trade_listed/<int:pokemon_id>/', views.trade_for_listed_pokemon_view, name='trade_for_listed_pokemon'),
    path('list/<int:pokemon_id>/', views.list_pokemon_for_sale_view, name='list_pokemon_for_sale'),
    path('send_trade_offer/<int:listing_id>/', views.send_trade_offer_view, name='send_trade_offer'),
    path('incoming_trade_offers/', views.incoming_trade_offers_view, name='incoming_trade_offers'),
    path('outgoing_trade_offers/', views.outgoing_trade_offers_view, name='outgoing_trade_offers'),
    path('accept_trade_offer/<int:offer_id>/', views.accept_trade_offer_view, name='accept_trade_offer'),
    path('decline_trade_offer/<int:offer_id>/', views.decline_trade_offer_view, name='decline_trade_offer'),
    path('trade_history/', views.trade_history_view, name='trade_history'),
]

