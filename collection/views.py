from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm   # added import
from django.contrib.auth import login  
from .models import Pokemon
from .models import TradeOffer

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
            continue
    coins = request.user.profile.coins
    listings = Pokemon.objects.filter(is_listed=True)
    return render(request, 'marketplace.html', {
        'pokemon_list': pokemon_list,
        'coins': coins,
        'listings': listings,
    })
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
    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally log in the user automatically:
            login(request, user)
            return redirect('collection')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def purchase_pokemon_view(request, pokemon_id):
    import pokebase as pb
    if request.method == "POST":
        # Check if the user has enough coins (cost: 1000)
        if request.user.profile.coins < 1000:
            # Optionally, you could add an error message here
            return redirect('marketplace')
        # Deduct cost and update profile
        request.user.profile.coins -= 1000
        request.user.profile.save()
        try:
            p = pb.pokemon(pokemon_id)
        except Exception as e:
            return redirect('marketplace')
        # Use the first type if available, otherwise "unknown"
        pokemon_type = p.types[0].type.name if p.types else "unknown"
        # Create a new Pokemon record in the user's collection
        Pokemon.objects.create(
            owner=request.user,
            name=p.name,
            type=pokemon_type,
            poke_id=pokemon_id,
        )
        return redirect('collection')
    else:
        return redirect('marketplace')
    
@login_required
def owned_pokemon_detail_view(request, pokemon_id):
    import pokebase as pb
    # Ensure the Pokémon belongs to the current user
    from django.shortcuts import get_object_or_404
    owned_pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
    try:
        # Fetch full details from the API based on the poke_id stored in your model
        p = pb.pokemon(owned_pokemon.poke_id)
        sprite = pb.SpriteResource('pokemon', owned_pokemon.poke_id, other=True, official_artwork=True)
    except Exception as e:
        return render(request, 'owned_pokemon_detail.html', {'error': str(e), 'pokemon': None})
    context = {
        'pokemon': p,
        'sprite_url': sprite.url,
        'user_pokemon': owned_pokemon,  # includes extra info like date_received
    }
    return render(request, 'owned_pokemon_detail.html', context)

@login_required
def list_pokemon_for_sale_view(request, pokemon_id):
    from django.shortcuts import get_object_or_404
    if request.method == 'POST':
        price = request.POST.get('price')
        try:
            price = int(price)
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            # If invalid, redirect back to the detail view
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
        pokemon.is_listed = True
        pokemon.price = price
        pokemon.save()
    return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)

@login_required
def listed_pokemon_detail_view(request, pokemon_id):
    """
    Display details for a Pokémon that is listed for sale/trade.
    If the current user is the seller, they can view their own details via owned_pokemon_detail_view.
    """
    import pokebase as pb
    from django.shortcuts import get_object_or_404
    # Get the listed Pokémon; only allow listings
    listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
    if listing.owner == request.user:
        # Redirect sellers to their personal detail view
        return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
    try:
        # Use the poke_id stored to fetch details from the API.
        p = pb.pokemon(listing.poke_id)
        sprite = pb.SpriteResource('pokemon', listing.poke_id, other=True, official_artwork=True)
    except Exception as e:
        return render(request, 'listed_pokemon_detail.html', {'error': str(e), 'pokemon': None})
    # Get the buyer's owned Pokémon in case they want to trade.
    owned_pokemon_list = Pokemon.objects.filter(owner=request.user)
    context = {
        'listing': listing,      # the listed Pokemon (seller, price, etc.)
        'pokemon': p,            # API data for the listed Pokemon
        'sprite_url': sprite.url,
        'owned_pokemon_list': owned_pokemon_list,  # for trade option
    }
    return render(request, 'listed_pokemon_detail.html', context)

@login_required
def purchase_listed_pokemon_view(request, pokemon_id):
    """
    Handle purchasing of a listed Pokémon.
    Deduct the asking price from the buyer, credit the seller, update ownership, and unlist the Pokémon.
    """
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
        # Prevent sellers from purchasing their own listings
        if listing.owner == request.user:
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        price = listing.price
        buyer_profile = request.user.profile
        seller_profile = listing.owner.profile
        if buyer_profile.coins < price:
            # Not enough coins; you can also add a message if desired.
            return redirect('listed_pokemon_detail', pokemon_id=pokemon_id)
        # Deduct price from buyer and credit seller
        buyer_profile.coins -= price
        buyer_profile.save()
        seller_profile.coins += price
        seller_profile.save()
        # Transfer ownership and unlist
        listing.owner = request.user
        listing.is_listed = False
        listing.price = None
        listing.save()
    return redirect('collection')

@login_required
def trade_for_listed_pokemon_view(request, pokemon_id):
    """
    Handle trading for a listed Pokémon.
    The buyer selects one of their own Pokémon for swapping.
    That Pokémon is transferred to the seller and the listed Pokémon is given to the buyer.
    """
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        offered_id = request.POST.get("owned_pokemon_id")
        listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
        # Buyer cannot trade for their own listing.
        if listing.owner == request.user:
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        offered_pokemon = get_object_or_404(Pokemon, id=offered_id, owner=request.user)
        seller = listing.owner
        # Swap the owners:
        listing.owner = request.user
        # Optionally, you might want to unlist the listing:
        listing.is_listed = False
        listing.price = None
        listing.save()
        # Give the offered Pokémon to the seller
        offered_pokemon.owner = seller
        offered_pokemon.save()
    return redirect('collection')

@login_required
def send_trade_offer_view(request, listing_id):
    """
    Buyer sends a trade offer for a listed Pokémon.
    Expects POST data with 'owned_pokemon_id' representing the buyer's offered Pokémon.
    """
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        offered_pokemon_id = request.POST.get("owned_pokemon_id")
        listing = get_object_or_404(Pokemon, id=listing_id, is_listed=True)
        # Ensure buyer is not the seller
        if listing.owner == request.user:
            return redirect('owned_pokemon_detail', pokemon_id=listing_id)
        offered_pokemon = get_object_or_404(Pokemon, id=offered_pokemon_id, owner=request.user)
        TradeOffer.objects.create(
            seller=listing.owner,
            buyer=request.user,
            listing=listing,
            offered_pokemon=offered_pokemon,
            status='pending'
        )
        return redirect('outgoing_trade_offers')
    else:
        return redirect('listed_pokemon_detail', pokemon_id=listing_id)

@login_required
def incoming_trade_offers_view(request):
    """
    Displays a list of pending trade offers for the current seller.
    """
    offers = TradeOffer.objects.filter(seller=request.user, status='pending')
    return render(request, 'incoming_trade_offers.html', {'offers': offers})

@login_required
def outgoing_trade_offers_view(request):
    """
    Displays a list of pending trade offers sent by the current user.
    """
    offers = TradeOffer.objects.filter(buyer=request.user, status='pending')
    return render(request, 'outgoing_trade_offers.html', {'offers': offers})

@login_required
def accept_trade_offer_view(request, offer_id):
    """
    Seller accepts a trade offer.
    This transfers the listed Pokémon to the buyer and the offered Pokémon to the seller, then marks the offer as accepted.
    """
    from django.shortcuts import get_object_or_404
    offer = get_object_or_404(TradeOffer, id=offer_id, seller=request.user, status='pending')
    # Transfer ownership:
    listing = offer.listing
    offered = offer.offered_pokemon
    seller = offer.seller
    buyer = offer.buyer
    listing.owner = buyer
    listing.is_listed = False
    listing.price = None
    listing.save()
    offered.owner = seller
    offered.save()
    offer.status = 'accepted'
    offer.save()
    return redirect('incoming_trade_offers')

@login_required
def decline_trade_offer_view(request, offer_id):
    """
    Seller declines a trade offer.
    """
    from django.shortcuts import get_object_or_404
    offer = get_object_or_404(TradeOffer, id=offer_id, seller=request.user, status='pending')
    offer.status = 'denied'
    offer.save()
    return redirect('incoming_trade_offers')