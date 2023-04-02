from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment", views.comment, name="comment"),
    path("bid", views.bid, name="bid"),
    path("end_listing", views.end_listing, name="end_listing"),
    path("categories", views.categories, name="categories"),
    path("<str:listing_id>", views.listing, name="listing_id"),
]
