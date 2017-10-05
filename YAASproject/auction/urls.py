from django.conf.urls import url
from . import views

app_name = 'auction'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<auctionID>[0-9]+)/$', views.detail, name='detail'),
    url(r'^search_form/$', views.search_form, name='search_form'),
]