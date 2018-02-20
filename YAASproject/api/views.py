from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from auction.models import Auction, Bid
from rest_framework import status
from datetime import datetime, timedelta
from .serializers import AuctionSerializer, AuctionsSerializer, Others, OthersSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import parser_classes
from django.contrib.auth import authenticate
from auction.views import bidEmailSening, bid_verifying
from decimal import Decimal
import base64


class AuctionsList(APIView):

    def get(self, request):
        auctions = None
        query1 = request.GET.get("count")
        query2 = request.GET.get("auction_title")
        if query1 and not query2:
            auctions = Auction.objects.filter(auction_status='Active').distinct().order_by('-id')[:int(query1)]
        if query2 and not query1:
            auctions = Auction.objects.filter(auction_title__icontains=query2, auction_status='Active').distinct().order_by('-id')
        if not query1 and not query2:
            auctions = Auction.objects.filter(auction_status='Active').order_by('-id')
        if query1 and query2:
            auctions = Auction.objects.filter(auction_title__icontains=query2, auction_status='Active').distinct().order_by('-id')[:int(query1)]

        serializer = AuctionsSerializer(auctions, many=True)
        return Response(serializer.data)

    def post(self):
        pass


class AuctionDetails(APIView):

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id, auction_status='Active')
        auction.currency = "EUR"
        serializer = AuctionSerializer(auction, many=False)
        diff = auction.ending_date.replace(tzinfo=None) - datetime.now()
        seconds = diff.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        other = Others(hours=hours, minutes=minutes)
        serializer2 = OthersSerializer(other, many=False)

        return Response({'auction_details': serializer.data,
        'time_remaining': serializer2.data,
    })


class BidOnAuction(APIView):
    @parser_classes((JSONParser,))
    def post(self, request, auction_id):
        info_au = self.request.META.get("HTTP_AUTHORIZATION", None)
        if info_au and info_au.startswith("Basic "):
            info_ba = info_au.split(" ", 1)[1]
            temp = base64.b64decode(info_ba)
            str = bytes.decode(temp)
            username, password = str.split(":")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auction_revision = ''
                    bidding_value = 0.00
                    try:
                        data = request.data
                        auction_revision = data['auction_revision']
                        bidding_value = round(Decimal.from_float(data['my_bid']), 2)
                    except:
                        return Response({'detail': 'Something wrong with your request.'}, status.HTTP_406_NOT_ACCEPTABLE)

                    if Auction.objects.filter(pk=auction_id, auction_status='Active').exists():
                        auction = Auction.objects.get(pk=auction_id)
                        error_message = bid_verifying(user, auction, auction_revision, bidding_value)
                        auction_delta = auction.ending_date.replace(tzinfo=None) - datetime.now()
                        expiry_check = auction_delta.total_seconds()
                        hours = int(expiry_check // 3600)
                        minutes = int((expiry_check % 3600) // 60)
                        if error_message !='':
                            return Response({'detail': error_message}, status.HTTP_406_NOT_ACCEPTABLE)
                        bid = Bid()
                        bid.bidding_value = bidding_value
                        bid.auction = auction
                        bid.bidder_name = user
                        count = Bid.objects.filter(auction=auction, bidder_name=user).count()
                        if (count > 0):
                            bid2 = Bid.objects.get(auction=auction, bidder_name=user)
                            bid2.bidding_value = bidding_value
                            bid2.save()
                        else:
                            bid.save()
                        # Soft deadlines
                        if (hours == 0 and minutes < 5):
                            auction.ending_date = auction.ending_date + timedelta(minutes=5)
                        auction.bidding_price = bidding_value
                        auction.winner_id = user.pk
                        auction.save()

                        bidEmailSening(auction_id)

                        return Response({'detail': 'Successful'}, status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'No active auction with this id'},
                                        status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Failed authorization'}, status.HTTP_403_FORBIDDEN)
            else:
                return Response({'detail': 'Failed authorization'}, status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Missing authorization'}, status.HTTP_403_FORBIDDEN)



