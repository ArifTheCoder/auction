from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


# Create user profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_language = models.CharField(max_length=20, default='en')


# get currency from api
class SetCurrency(models.Model):
    currency = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=19, decimal_places=4)


# save auction data
class Auction(models.Model):
    Set_Status = (
        ('Active', 'Active'),
        ('Banned', 'Banned'),
        ('Due', 'Due'),
        ('Adjudicated', 'Adjudicated'),
    )
    seller_name = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_title = models.CharField(max_length=600)
    description = models.CharField(max_length=5000)
    currency = models.CharField(max_length=20)
    token_edit = models.CharField(max_length=600)
    starting_price = models.DecimalField(max_length=30, max_digits=19, decimal_places=2)
    bidding_price = models.DecimalField(max_length=30, max_digits=19, decimal_places=2, null=True)
    winner_id = models.IntegerField(null=True)
    starting_date = models.DateTimeField(blank=True)
    auction_duration_hours = models.IntegerField(default=72, validators=[MinValueValidator(72)])
    ending_date = models.DateTimeField(blank=True)
    auction_status = models.CharField(max_length=20, choices=Set_Status, default='Active')
    auction_revision = models.IntegerField(default=1)

    def __str__(self):
        return self.auction_title


# bid data saving
class Bid(models.Model):
    bidder_name = models.ForeignKey(User, on_delete=models.CASCADE)
    bidding_value = models.DecimalField(max_length=30, max_digits=19, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return self.bidder_name.username

