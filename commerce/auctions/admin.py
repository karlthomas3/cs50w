from django.contrib import admin

from .models import User, Listing, Bid, Comment, Category

class ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watching",)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
