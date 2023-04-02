from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Listing(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings", default=None
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, related_name="listings"
    )
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=280)
    pic_url = models.URLField(blank=True)
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2, default=00.01)
    current_price = models.DecimalField(max_digits=6, decimal_places=2, default=00.01)
    watching = models.ManyToManyField(User, blank=True, related_name="watching")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"User: {self.user} Item:{self.item} Amount: {self.amount}"

    class Meta:
        unique_together = ("user", "item")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=280)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return f"User:{self.user} Comment:{self.text}"
