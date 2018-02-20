from django.conf.urls import url
from . import views

app_name = 'auction'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auction/$', views.myAuction, name='myAuction'),
    url(r'^search/$', views.search, name='search'),
    url(r'^banned/$', views.searchBanned, name='banned'),
    url(r'^(?P<auction_id>[0-9]+)/$', views.auctionDetails, name='detail'),
    url(r'^auction/add/$', views.createAuction, name='auction-add'),
    url(r'^auction/confirm/$', views.auctionConfirm, name='auction-confirm'),
    url(r'^auction/(?P<pk>[0-9]+)/edit/$', views.EditAuctionView.as_view(), name='edit-auction'),
    url(r'^language/$', views.setLanguage, name='language'),
    url(r'^auction/(?P<pk>[0-9]+)/ban/$', views.banAuction, name='ban-auction'),
    url(r'^auction/(?P<pk>[0-9]+)/unban/$', views.unbanAuction, name='unban-auction'),
    url(r'^auction/(?P<auction_id>[0-9]+)/bid/$', views.BidFormFormView.as_view(), name='bid'),
    url(r'^auction/non/edit/(?P<token_edit>[\w\-]+)/$', views.AuctionEditFormNonView.as_view(), name='auction-edit-without'),
]