
from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    date_received = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pokemons')

    def __str__(self):
        return f"{self.name} ({self.type})"

# Create your models here.
