from django.shortcuts import render, get_object_or_404, redirect
from .models import Pokemon

def collection_view(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'name')  # Default to sorting by name

    # Start with Pokémon owned by the logged-in user
    pokemons = Pokemon.objects.filter(owner=request.user)

    # If a search query is present, filter further
    if search_query:
        pokemons = pokemons.filter(name__icontains=search_query)

    # Sorting logic
    if sort_by == 'name':
        pokemons = pokemons.order_by('name')
    elif sort_by == 'type':
        pokemons = pokemons.order_by('type')
    elif sort_by == 'date':
        pokemons = pokemons.order_by('date_received')

    return render(request, 'collection.html', {
        'pokemons': pokemons,
        'search_query': search_query,
        'sort_by': sort_by,  # Pass the selected sort option to the template
    })

def toggle_favorite(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
    pokemon.is_favorite = not pokemon.is_favorite
    pokemon.save()
    return redirect('collection')
