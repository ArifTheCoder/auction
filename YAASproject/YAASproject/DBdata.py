from django.contrib.auth.models import User
from decimal import Decimal
from auction.models import *
from django.utils import timezone
from auction.views import get_random_string
from datetime import timedelta


class DBdataGenerator:
    # add user to database
    def add_user(self, value):
        user = User()
        user.username = 'user' + str(value)
        user.email = 'user' + str(value) + '@yaas.com'
        password = 'pass' + str(value)
        user.set_password(password)
        user.save()
        profile = Profile()
        profile.profile_language = 'en'
        profile.user = user
        profile.save()

    # Add auction to database
    def add_auction(self, value):
        auction = Auction()
        auction.auction_title = "auction title " + str(value)
        auction.description = "description of item " + str(value)
        #auction.auction_duration_hours = random.randint(72, 200)
        auction.auction_duration_hours = int(72)
        auction.starting_price = Decimal(0.05)
        auction.seller_name = User.objects.get(username="user" + str(value))
        auction.starting_date = timezone.now()
        auction.ending_date = auction.starting_date + timedelta(hours=auction.auction_duration_hours)
        auction.token_edit = auction.starting_date.strftime('%Y%m%d%H%M%S') + get_random_string()
        auction.auction_revision = 1
        auction.save()

    # Add bid to database
    def add_bid(self, value):
        bid = Bid()
        auction = Auction.objects.get(auction_title="title " + str(51 - value))
        bid.bidding_value = Decimal(0.06)
        bid.auction = auction
        bid.bidder_name = User.objects.get(username="user" + str(value + 1))
        bid.save()
        auction.winner_id = User.objects.get(username="user" + str(value + 1)).id
        auction.bidding_price = bid.bidding_value
        auction.save()

    def data_generate(self):

        for value in range(1, 51):
            self.add_user(value)
        for value in range(1, 51):
            self.add_auction(value)
        for value in range(1, 11):
            self.add_bid(value)

