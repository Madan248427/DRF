from django.db import models

# Create your models here.
from django.db import models


# Decorative Items
# Religious Artifacts
# Handicrafts
# Musical Instruments
# Home & Living
# Antiques & Collectibles
# Garden & Outdoor
# Spiritual & Wellness
# Gifts & Festive Items
# Traditional Kitchenware
class Product(models.Model):
    Product_Catagory=(
        ('decor','Decorative Items'),
        ('religious','Religious Artifacts'),
        ('handicraft','Handicrafts'),
        ('musical','Musical Instruments'),
        ('antique','Antiques & Collectibles'),
        ('others','Others'),

    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    company=models.CharField(blank=True,max_length=100)
    stock = models.IntegerField()
    category = models.CharField(choices=Product_Catagory,max_length=50)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return self.name

    
    