from django.contrib import admin
from .models import Pokemon, Profile, TradeOffer

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_favorite', 'date_received', 'owner', 'is_listed', 'price')
    search_fields = ('name', 'type', 'owner__username')
    list_filter = ('is_favorite', 'type', 'is_listed')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'coins')
    search_fields = ('user__username',)

@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'listing', 'offered_pokemon', 'status', 'created_at')
    search_fields = ('buyer__username', 'seller__username', 'listing__name', 'offered_pokemon__name')
    list_filter = ('status', 'created_at')
