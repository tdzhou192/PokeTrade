from django.shortcuts import render
from .models import Pokemon


def collection_view(request):
    # Get all the Pokémon for the logged-in user
    pokemons = Pokemon.objects.all()

    return render(request, 'collection.html', {'pokemons': pokemons})


from django.shortcuts import render

# Create your views here.
