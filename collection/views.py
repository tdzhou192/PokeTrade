from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList

from .forms import CustomUserCreationForm, CustomErrorList
from .models import Pokemon, TradeOffer

User = get_user_model()

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def login_view(request):
    template_data = {}
    template_data['title'] = 'Login'

    if request.method == 'GET':
        return render(request, 'registration/login.html', {'template_data': template_data})

    elif request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('collection')
        else:
            template_data['error'] = 'The email or password is incorrect.'
            return render(request, 'registration/login.html', {'template_data': template_data})

def collection_view(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'name')

    pokemons = Pokemon.objects.filter(owner=request.user.id)

    if search_query:
        pokemons = pokemons.filter(name__icontains=search_query)

    if sort_by == 'name':
        pokemons = pokemons.order_by('name')
    elif sort_by == 'type':
        pokemons = pokemons.order_by('type')
    elif sort_by == 'date':
        pokemons = pokemons.order_by('date_received')
    elif sort_by == 'favorite':
        pokemons = pokemons.order_by('-is_favorite', 'name')

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
    # Get the search query parameter
    search_query = request.GET.get('search', '')
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
    if search_query:
        listings = Pokemon.objects.filter(is_listed=True, name__icontains=search_query)
    else:
        listings = Pokemon.objects.filter(is_listed=True)
    return render(request, 'marketplace.html', {
        'pokemon_list': pokemon_list,
        'coins': coins,
        'listings': listings,
        'search_query': search_query,
    })

@login_required
def trade_pokemon_view(request, marketplace_id):
    import pokebase as pb
    from .models import Pokemon
    if request.method == "POST":
        owned_pokemon_id = request.POST.get("owned_pokemon_id")
        try:
            owned_pokemon = Pokemon.objects.get(id=owned_pokemon_id, owner=request.user)
        except Pokemon.DoesNotExist:
            return redirect('collection')
        try:
            marketplace_pokemon = pb.pokemon(marketplace_id)
            if marketplace_pokemon.types:
                marketplace_type = marketplace_pokemon.types[0].type.name
            else:
                marketplace_type = "unknown"
        except Exception as e:
            return redirect('collection')

        owned_pokemon.name = marketplace_pokemon.name
        owned_pokemon.type = marketplace_type
        owned_pokemon.poke_id = marketplace_id
        owned_pokemon.save()

        return redirect('collection')
    else:
        return redirect('collection')



@login_required
def populate_collection(request):
    import pokebase as pb
    import random
    from .models import Pokemon
    if request.method == "POST":
         for i in range(5):
              random_id = random.randint(1, 151)
              try:
                  p = pb.pokemon(random_id)
                  pokemon_type = p.types[0].type.name if p.types else "unknown"
                  Pokemon.objects.create(
                       owner=request.user,
                       name=p.name,
                       type=pokemon_type,
                       poke_id=random_id,
                  )
              except Exception as e:
                  continue
         return redirect('collection')
    else:
         return redirect('collection')
    
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)  # Correct usage
            return redirect('collection')
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})




@login_required
def purchase_pokemon_view(request, pokemon_id):
    import pokebase as pb
    if request.method == "POST":
        if request.user.profile.coins < 1000:
            return redirect('marketplace')
        request.user.profile.coins -= 1000
        request.user.profile.save()
        try:
            p = pb.pokemon(pokemon_id)
        except Exception as e:
            return redirect('marketplace')
        pokemon_type = p.types[0].type.name if p.types else "unknown"
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
    from django.shortcuts import get_object_or_404
    owned_pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
    try:
        p = pb.pokemon(owned_pokemon.poke_id)
        sprite = pb.SpriteResource('pokemon', owned_pokemon.poke_id, other=True, official_artwork=True)
    except Exception as e:
        return render(request, 'owned_pokemon_detail.html', {'error': str(e), 'pokemon': None})
    context = {
        'pokemon': p,
        'sprite_url': sprite.url,
        'user_pokemon': owned_pokemon,
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
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        pokemon = get_object_or_404(Pokemon, id=pokemon_id, owner=request.user)
        pokemon.is_listed = True
        pokemon.price = price
        pokemon.save()
    return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)

@login_required
def listed_pokemon_detail_view(request, pokemon_id):
    import pokebase as pb
    from django.shortcuts import get_object_or_404
    listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
    if listing.owner == request.user:
        return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
    try:
        p = pb.pokemon(listing.poke_id)
        sprite = pb.SpriteResource('pokemon', listing.poke_id, other=True, official_artwork=True)
    except Exception as e:
        return render(request, 'listed_pokemon_detail.html', {'error': str(e), 'pokemon': None})
    owned_pokemon_list = Pokemon.objects.filter(owner=request.user)
    context = {
        'listing': listing,
        'pokemon': p,
        'sprite_url': sprite.url,
        'owned_pokemon_list': owned_pokemon_list,
    }
    return render(request, 'listed_pokemon_detail.html', context)

from django.urls import reverse


@login_required
def purchase_listed_pokemon_view(request, pokemon_id):
    from django.shortcuts import get_object_or_404
    from .models import Purchase
    if request.method == "POST":
        listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
        if listing.owner == request.user:
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        price = listing.price
        buyer_profile = request.user.profile
        seller_profile = listing.owner.profile
        if buyer_profile.coins < price:
            return redirect(reverse('listed_pokemon_detail', args=[pokemon_id]) + "?insufficient_funds=1")
        buyer_profile.coins -= price
        buyer_profile.save()
        seller_profile.coins += price
        seller_profile.save()
        prev_seller = listing.owner
        listing.owner = request.user
        listing.is_listed = False
        listing.price = None
        listing.save()
        Purchase.objects.create(
            buyer=request.user,
            seller=prev_seller,
            pokemon=listing,
            price=price,
        )
    return redirect('collection')

@login_required
def trade_for_listed_pokemon_view(request, pokemon_id):
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        offered_id = request.POST.get("owned_pokemon_id")
        listing = get_object_or_404(Pokemon, id=pokemon_id, is_listed=True)
        if listing.owner == request.user:
            return redirect('owned_pokemon_detail', pokemon_id=pokemon_id)
        offered_pokemon = get_object_or_404(Pokemon, id=offered_id, owner=request.user)
        seller = listing.owner
        listing.owner = request.user
        listing.is_listed = False
        listing.price = None
        listing.save()
        offered_pokemon.owner = seller
        offered_pokemon.save()
    return redirect('collection')

@login_required
def send_trade_offer_view(request, listing_id):
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        offered_pokemon_id = request.POST.get("owned_pokemon_id")
        listing = get_object_or_404(Pokemon, id=listing_id, is_listed=True)
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
    offers = TradeOffer.objects.filter(seller=request.user, status='pending')
    return render(request, 'incoming_trade_offers.html', {'offers': offers})

@login_required
def outgoing_trade_offers_view(request):
    offers = TradeOffer.objects.filter(buyer=request.user, status='pending')
    return render(request, 'outgoing_trade_offers.html', {'offers': offers})

@login_required
def accept_trade_offer_view(request, offer_id):
    from django.shortcuts import get_object_or_404
    offer = get_object_or_404(TradeOffer, id=offer_id, seller=request.user, status='pending')
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
    from django.shortcuts import get_object_or_404
    offer = get_object_or_404(TradeOffer, id=offer_id, seller=request.user, status='pending')
    offer.status = 'denied'
    offer.save()
    return redirect('incoming_trade_offers')

@login_required
def trade_history_view(request):
    from django.db.models import Q
    from .models import Purchase
    trade_offers = TradeOffer.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user),
        status='accepted'
    )
    purchases = Purchase.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    history = []
    for t in trade_offers:
        history.append({
            'type': 'trade',
            'created_at': t.created_at,
            'data': t,
        })
    for p in purchases:
        event_type = 'purchase' if p.buyer == request.user else 'sale'
        history.append({
            'type': event_type,
            'created_at': p.created_at,
            'data': p,
        })
    history.sort(key=lambda x: x['created_at'], reverse=True)
    return render(request, 'trade_history.html', {'history': history})

@login_required
def purchase_pokemon_view(request, pokemon_id):
    import pokebase as pb
    from .models import Purchase
    if request.method == "POST":
        if request.user.profile.coins < 1000:
            return redirect('marketplace')
        request.user.profile.coins -= 1000
        request.user.profile.save()
        try:
            p = pb.pokemon(pokemon_id)
        except Exception as e:
            return redirect('marketplace')
        pokemon_type = p.types[0].type.name if p.types else "unknown"
        new_pokemon = Pokemon.objects.create(
            owner=request.user,
            name=p.name,
            type=pokemon_type,
            poke_id=pokemon_id,
        )
        Purchase.objects.create(
            buyer=request.user,
            seller=None,
            pokemon=new_pokemon,
            price=1000
        )
        return redirect('collection')
    else:
        return redirect('marketplace')



def about_view(request):
    return render(request, 'about.html')