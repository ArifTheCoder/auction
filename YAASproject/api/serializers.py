from auction.models import Auction
from rest_framework import serializers


class Others(object):
    def __init__(self, hours, minutes):
        self.hours = hours
        self.minutes = minutes


class AuctionSerializer(serializers.ModelSerializer):
    bid_set = serializers.StringRelatedField(many=True)
    seller_name = serializers.ReadOnlyField(source='seller_name.username')

    class Meta:
        model = Auction
        fields = ('id', 'auction_title', 'description', 'auction_revision', 'starting_price', 'bidding_price', 'currency', 'ending_date', 'seller_name', 'bid_set')


class AuctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'auction_title', 'ending_date')


class OthersSerializer(serializers.Serializer):
    hours = serializers.IntegerField()
    minutes = serializers.IntegerField()






