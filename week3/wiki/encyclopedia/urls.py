from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.title, name="title"),
    path("create", views.create, name="create"),
    path("r_page", views.random_page, name="r_page"),
    path("exist", views.create, name="exist"),
    path("edit", views.edit_page, name="edit"),
]
