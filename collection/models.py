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

# Add signals to automatically create a Profile when a new user is created:
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()