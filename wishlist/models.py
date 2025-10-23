from django.db import models
from user_profile.models import BuyerProfile
from seller.models import ProductEntry

# Create your models here.

class WishlistItem(models.Model):
    user = models.ManyToManyField(BuyerProfile, related_name="wishlists")
    products = models.ManyToManyField(ProductEntry, related_name="wishlist_items")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name