from django.views.decorators.csrf import csrf_exempt
from . import views
from django.conf.urls import url


app_name = 'api'

urlpatterns = [
    url(r'^auction/$', views.AuctionsList.as_view()),
    url(r'^auction/(?P<auction_id>[0-9]+)/$', views.AuctionDetails.as_view()),
    url(r'^auction/(?P<auction_id>[0-9]+)/bid/$', csrf_exempt(views.BidOnAuction.as_view())),
]
