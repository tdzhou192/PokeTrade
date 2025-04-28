from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    date_received = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pokemons')
    poke_id = models.IntegerField(null=True, blank=True)   
    is_listed = models.BooleanField(default=False)
    price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    coins = models.IntegerField(default=5000)

    def __str__(self):
        return f"{self.user.username}'s profile"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class TradeOffer(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='incoming_trade_offers'
    )
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='outgoing_trade_offers'
    )
    listing = models.ForeignKey(
        Pokemon, on_delete=models.CASCADE, related_name='trade_offers'
    )
    offered_pokemon = models.ForeignKey(
        Pokemon, on_delete=models.CASCADE, related_name='offered_in_trade'
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TradeOffer from {self.buyer.username} for {self.listing.name} ({self.status})"
    
class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    price = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pokemon.name} purchased by {self.buyer.username}"