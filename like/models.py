from django.db import models
from user_profile.models import BuyerProfile
from seller.models import ProductEntry

class Like(models.Model):
    user = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductEntry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.user.username} likes {self.product.product_name}"

