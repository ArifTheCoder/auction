from django.test import TestCase
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.test.client import Client
from YAASproject.views import generate_test_db
from auction.models import *


class AuctionTest(TestCase):

    def setUp(self):
        generate_test_db()
        self.user = User()
        self.user.username = 'testuser'
        self.user.email = 'testuser@example.com'
        self.user.set_password('testuser1234')
        self.user.save()
        self.profile = Profile()
        self.profile.user = self.user
        self.profile.profile_language = 'en'
        self.profile.save()

    def test_create_auction_without_authentication(self):
        resp = self.client.post(reverse('auction:auction-add'),
                                {'auction_title': 'TestAuction', 'description': 'Auction Description',
                                 'auction_duration_hours': int(77),
                                 'starting_price': 0.02})
        self.assertEqual(resp.status_code, 302)

    def test_create_auction_with_authentication(self):

        self.client.login(username='testuser', password='testuser1234')
        prevcount = Auction.objects.count()

        resp = self.client.post(reverse('auction:auction-add'),
                                {'auction_title': 'TestAuction', 'description': 'Auction Description',
                                 'auction_duration_hours': int(71),
                                 'starting_price': 0.02})

        self.assertEqual(prevcount, Auction.objects.count())

        resp = self.client.post(reverse('auction:auction-add'),
                                {'auction_title': 'TestAuction', 'description': 'Auction Description',
                                 'auction_duration_hours': int(77),
                                 'starting_price': 0.02})

        self.failUnlessEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "auction/confirm_auction.html")

        resp = self.client.post(reverse('auction:auction-confirm'),
                                {'confirm': 'False'})
        self.failUnlessEqual(resp.status_code, 302)
        self.assertEqual(prevcount, Auction.objects.count())

        resp = self.client.post(reverse('auction:auction-confirm'),
                                {'confirm': 'True'})
        self.assertEqual(prevcount + 1, Auction.objects.count())
        latest_auction = Auction.objects.latest('starting_date')
        self.assertEqual(latest_auction.auction_title, 'TestAuction')


class TestBid(TestCase):

    def setUp(self):
        generate_test_db()

        self.user = User()
        self.user.username = 'testuser'
        self.user.email = 'testuser@example.com'
        self.user.set_password('testuser1234')
        self.user.save()
        self.profile = Profile()
        self.profile.user = self.user
        self.profile.profile_language = 'en'
        self.profile.save()
        self.user2 = User()
        self.user2.username = 'testuser2'
        self.user2.email = 'testuser2@example.com'
        self.user2.set_password('testuser21234')
        self.user2.save()
        self.profile2 = Profile()
        self.profile2.user = self.user2
        self.profile2.profile_language = 'en'
        self.profile2.save()

        self.auction = Auction.objects.get(auction_title='auction title 1')
        self.auction_banned = Auction.objects.get(auction_title='auction title 2')
        self.auction_banned.auction_status = 'Banned'
        self.auction_banned.save()

    def test_place_bid_without_authentication(self):
        prevcount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01),2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevcount, Bid.objects.count())

    def test_place_bid_with_authentication_succesfully(self):
        self.client.login(username='testuser', password='testuser1234')
        prevcount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevcount + 1, Bid.objects.count())

    def test_fail_bid_dueTo_equal_than_start_price(self):
        self.client.login(username='testuser', password='testuser1234')
        prevCount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price, 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_fail_bid_dueTo_less_than_start_price(self):
        self.client.login(username='testuser', password='testuser1234')
        prevCount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price - Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_fail_bid_dueTo_already_winning(self):
        self.client.login(username='testuser', password='testuser1234')
        prevCount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount+1, Bid.objects.count())
        prevCount = Bid.objects.count()
        bidding_value = round(bidding_value + Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_fail_bid_dueTo_bidder_equalTo_seller(self):
        self.client.login(username='user1', password='pass1')
        prevCount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_fail_bid_dueTo_non_active_auction(self):
        self.client.login(username='user1', password='pass1')
        prevCount = Bid.objects.count()
        auction_id = str(self.auction_banned.id)
        revision_bid = str(self.auction_banned.auction_revision)
        bidding_value = round(self.auction_banned.starting_price + Decimal(0.01), 2)
        resp = self.client.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_bid_concurrency_for_description_update(self):

        c1 = Client()
        c1.login(username='testuser', password='testuser1234')

        old_auction = self.auction

        resp = self.client.post(reverse('auction:auction-edit-without', args=(self.auction.token_edit,)),
                        {'description': 'Description2'
                         })

        prevCount = Bid.objects.count()
        auction_id = str(old_auction.id)
        revision_bid = str(old_auction.auction_revision)
        bidding_value = round(old_auction.starting_price + Decimal(0.01), 2)
        resp = c1.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

    def test_bid_concurrency_for_another_user_bid(self):
        c1 = Client()
        c1.login(username='testuser', password='testuser1234')
        c2 = Client()
        c2.login(username='testuser2', password='testuser21234')

        prevCount = Bid.objects.count()
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01), 2)
        if self.auction.bidding_price:
            bidding_value = round(self.auction.bidding_price + Decimal(0.01), 2)
        resp = c1.post(reverse('auction:bid', args=(auction_id,)),
                                {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount + 1, Bid.objects.count())

        prevCount = Bid.objects.count()
        resp = c2.post(reverse('auction:bid', args=(auction_id,)),
                       {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount, Bid.objects.count())

        prevCount = Bid.objects.count()
        self.auction = Auction.objects.get(auction_title='auction title 1')
        auction_id = str(self.auction.id)
        revision_bid = str(self.auction.auction_revision)
        bidding_value = round(self.auction.starting_price + Decimal(0.01), 2)
        if self.auction.bidding_price:
            bidding_value = round(self.auction.bidding_price + Decimal(0.01), 2)
        resp = c2.post(reverse('auction:bid', args=(auction_id,)),
                       {'auction_revision': revision_bid, 'bidding_value': bidding_value})
        self.assertEqual(prevCount + 1, Bid.objects.count())











