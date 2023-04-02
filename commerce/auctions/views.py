from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms


from .models import User, Category, Listing, Bid, Comment


class NewListingForm(forms.ModelForm):
    starting_bid = forms.DecimalField(decimal_places=2, initial=0.01)

    class Meta:
        model = Listing
        fields = ["category", "name", "description", "pic_url", "starting_bid"]


def index(request):
    return render(request, "auctions/index.html", {"listings": Listing.objects.all()})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):
    try:
        # try to find listing by id, check if current user has listing in watchlist, and retreive the current highest bid
        listing = Listing.objects.get(id=listing_id)
        watching = listing.watching.filter(id=request.user.id) or None
        highest = Bid.objects.get(amount=listing.current_price).user
    except Listing.DoesNotExist:
        raise Http404("Listing not found")
    except Bid.DoesNotExist:
        highest = listing.seller

    # feed page listing and other variables
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "comments": listing.comments.all(),
            "watching": watching,
            "highest": highest,
        },
    )


def create(request):
    # if form is submitted, save as  new listing
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.current_price = form.cleaned_data["starting_bid"]
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        # or just make a new form
        form = NewListingForm(initial={"seller": request.user})
    return render(request, "auctions/create.html", {"form": form})


def comment(request):
    if request.method == "POST":
        # save new comments when submitted
        listing = Listing.objects.get(id=request.POST["listing"])
        n_comment = Comment()
        n_comment.user = request.user
        n_comment.text = request.POST["text"]
        n_comment.listing = listing
        n_comment.save()
        return HttpResponseRedirect(reverse("listing_id", args=[listing.id]))


def watchlist(request):
    if request.method == "POST":
        # check whether user has watchlisted item and either add or remove watchlist
        next = request.POST.get("next", "/")
        listing = Listing.objects.get(id=request.POST["watch_item"])
        watcher = listing.watching.filter(id=request.user.id) or None
        if watcher:
            listing.watching.remove(request.user)
        else:
            listing.watching.add(request.user)

        return HttpResponseRedirect(next)

    try:
        user = request.user
    except User.DoesNotExist:
        return render(
            request, "auctions/login.html", {"message": "Log in to view watchlist"}
        )

    return render(request, "auctions/watchlist.html", {"watching": user.watching.all()})


def bid(request):
    print(request)
    if request.method == "POST":
        # grab relevant data
        next = request.POST.get("next", "/")
        listing = Listing.objects.get(id=request.POST["listing"])
        user = User.objects.get(username=request.user)

        # just incase they dont input anything
        try:
            new_price = float(request.POST["bid"])
        except ValueError:
            new_price = 0

        message = None
        # update current price if new bid is higher
        if new_price > listing.current_price:
            listing.current_price = new_price
            listing.save()
            try:
                # update users previous bid
                old_bid = listing.bids.get(user=user)
                old_bid.amount = new_price
                old_bid.save()
            except Bid.DoesNotExist:
                # if no previous bid then create one
                new_bid = Bid()
                new_bid.user = user
                new_bid.amount = new_price
                new_bid.item = listing
                new_bid.save()
        else:
            message = "New bid must be higher than current bid."

        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listing,
                "comments": listing.comments.all(),
                "watching": listing.watching.filter(id=request.user.id) or None,
                "message": message,
            },
        )
    return HttpResponseRedirect(reverse("watchlist"))


def end_listing(request):
    if request.method == "POST":
        # fetch the listing and set active to False
        next = request.POST.get("next", "/")
        listing = Listing.objects.get(id=request.POST["listing"])
        listing.active = False
        listing.save()

    return HttpResponseRedirect(next)


def categories(request):
    # list all categories
    categories = Category.objects.all()
    listings = None
    # list all items in a selected category
    if request.method == "POST":
        category = Category.objects.get(name=request.POST["category"])
        listings = Listing.objects.filter(category=category)
        print(listings)

    return render(
        request,
        "auctions/category.html",
        {"categories": categories, "listings": listings},
    )
