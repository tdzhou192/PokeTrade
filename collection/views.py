from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Pokemon

@login_required
def collection_view(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'name')

    pokemons = Pokemon.objects.filter(owner=request.user)

    if search_query:
        pokemons = pokemons.filter(name__icontains=search_query)

    if sort_by == 'name':
        pokemons = pokemons.order_by('name')
    elif sort_by == 'type':
        pokemons = pokemons.order_by('type')
    elif sort_by == 'date':
        pokemons = pokemons.order_by('date_received')

    return render(request, 'collection.html', {
        'pokemons': pokemons,
        'search_query': search_query,
        'sort_by': sort_by,
    })

@login_required
def toggle_favorite(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
    pokemon.is_favorite = not pokemon.is_favorite
    pokemon.save()
    return redirect('collection')

@login_required
def marketplace_view(request):
    import pokebase as pb
    pokemon_list = []
    # Fetch the first 20 Pokémon from the API
    for i in range(1, 21):
        try:
            p = pb.pokemon(i)
            sprite = pb.SpriteResource('pokemon', i, other=True, official_artwork=True)
            pokemon_list.append({
                'id': i,
                'name': p.name,
                'sprite_url': sprite.url,
            })
        except Exception as e:
            # If an error occurs (for example, API limits), skip this Pokémon
            continue
    return render(request, 'marketplace.html', {'pokemon_list': pokemon_list})

# ... existing code above remains unchanged ...

@login_required
def pokemon_detail_view(request, pokemon_id):
    import pokebase as pb
    from .models import Pokemon
    try:
        # Fetch marketplace Pokémon data from PokeAPI
        pokemon = pb.pokemon(pokemon_id)
        sprite = pb.SpriteResource('pokemon', pokemon_id, other=True, official_artwork=True)
    except Exception as e:
        return render(request, 'pokemon_detail.html', {'error': str(e), 'pokemon': None})
    # Also fetch your owned Pokémon in random order for potential trade
    owned_pokemon_list = Pokemon.objects.filter(owner=request.user).order_by('?')
    context = {
        'pokemon': pokemon,
        'sprite_url': sprite.url,
        'owned_pokemon_list': owned_pokemon_list,
    }
    return render(request, 'pokemon_detail.html', context)

@login_required
def trade_pokemon_view(request, marketplace_id):
    import pokebase as pb
    from .models import Pokemon
    if request.method == "POST":
        owned_pokemon_id = request.POST.get("owned_pokemon_id")
        try:
            # Get the Pokémon you own to trade away
            owned_pokemon = Pokemon.objects.get(id=owned_pokemon_id, owner=request.user)
        except Pokemon.DoesNotExist:
            return redirect('collection')
        try:
            # Fetch the marketplace Pokémon data using PokeAPI
            marketplace_pokemon = pb.pokemon(marketplace_id)
            # Get the type from the marketplace Pokémon; take the first type if present.
            if marketplace_pokemon.types:
                marketplace_type = marketplace_pokemon.types[0].type.name
            else:
                marketplace_type = "unknown"
        except Exception as e:
            return redirect('collection')

        # Perform the trade: update your owned Pokémon record with marketplace Pokémon details.
        owned_pokemon.name = marketplace_pokemon.name
        owned_pokemon.type = marketplace_type
        owned_pokemon.poke_id = marketplace_id  # <-- update the poke_id to reflect the new Pokémon
        owned_pokemon.save()

        # Redirect to your collection view after the trade
        return redirect('collection')
    else:
        return redirect('collection')



@login_required
def populate_collection(request):
    import pokebase as pb
    import random
    from .models import Pokemon
    if request.method == "POST":
         # Add 5 random Pokémon to the user's collection.
         for i in range(5):
              random_id = random.randint(1, 151)
              try:
                  p = pb.pokemon(random_id)
                  # Use the first type if available.
                  pokemon_type = p.types[0].type.name if p.types else "unknown"
                  # Create a new Pokémon record.
                  Pokemon.objects.create(
                       owner=request.user,
                       name=p.name,
                       type=pokemon_type,
                       poke_id=random_id,  # store the PokeAPI id so we can build the image URL later
                  )
              except Exception as e:
                  # If an error occurs (e.g. API error), skip this one.
                  continue
         # Redirect back to your collection view.
         return redirect('collection')
    else:
         # For non-POST requests, simply redirect back.
         return redirect('collection')