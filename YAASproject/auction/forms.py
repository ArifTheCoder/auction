from django import forms
from .models import Auction, Bid


# auction form blueprint
class AuctionForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ['auction_title', 'description', 'starting_price', 'auction_duration_hours']
        widgets = {'description': forms.Textarea(attrs={'rows': 5}), }


# Edit auction form
class EditAuctionForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ['description']
        widgets = {'description': forms.Textarea(attrs={'rows': 5}), }


# Bidding form
class BiddingForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['bidding_value']

