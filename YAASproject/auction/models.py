from django.db import models

# Create your models here.
class Auction(models.Model):
    seller = models.CharField(max_length=200)
    auctionTitle = models.CharField(max_length=600)
    description = models.CharField(max_length=2500)
    currentPrice = models.FloatField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.auctionTitle