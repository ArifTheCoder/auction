from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from .forms import AuctionForm, EditAuctionForm, BiddingForm
from .models import Auction, Bid, Profile, SetCurrency
from datetime import timedelta
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
import threading
import time
from django.core.mail import EmailMessage
from decimal import Decimal
import requests

# Create your views here.
currency_list = [{'name':'Australian Dollar','value':'AUD'},
{'name':'Euros','value':'EUR'},
{'name':'Bulgarian Lev','value':'BGN'},
{'name':'Brazilian Real','value':'BRL'},
{'name':'Canadian Dollar','value':'CAD'},
{'name':'Swiss Franc','value':'CHF'},
{'name':'Renminbi(Yuan)','value':'CNY'},
{'name':'Czech Koruna','value':'CZK'},
{'name':'Danish Krone','value':'DKK'},
{'name':'Pound Sterling','value':'GBP'},
{'name':'HK Dollar','value':'HKD'},
{'name':'Croatian Kuna','value':'HRK'},
{'name':'Forint','value':'HUF'},
{'name':'Rupiah','value':'IDR'},
{'name':'Israeli Sheqel','value':'ILS'},
{'name':'Indian Rupee','value':'INR'},
{'name':'Yen','value':'JPY'},
{'name':'Won','value':'KRW'},
{'name':'Mexican Peso','value':'MXN'},
{'name':'Malaysian Ringgit','value':'MYR'},
{'name':'Norwegian Krone','value':'NOK'},
{'name':'NZ Dollar','value':'NZD'},
{'name':'Philippine Peso','value':'PHP'},
{'name':'Zloty','value':'PLN'},
{'name':'Russian Ruble','value':'RUB'},
{'name':'Swedish Krona','value':'SEK'},
{'name':'Singapore Dollar','value':'SGD'},
{'name':'Thai Baht','value':'THB'},
{'name':'Turk Lira','value':'TRY'},
{'name':'US Dollar','value':'USD'},
{'name':'Rand','value':'ZAR'}]


# get price from database
def exchangeCurrency(currency):
    currency_value = 1.0000
    if currency != 'EUR':
        if SetCurrency.objects.filter(currency=currency).exists():
            cur = SetCurrency.objects.get(currency=currency)
            currency_value = float(cur.value)
    return currency_value


# Language change
@csrf_exempt
def setLanguage(request):
    q = request.POST.get("lang")
    if (q == ''):
        return redirect('auction:index')
    if (q == 'en' or q == 'sv' or q == 'fi'):
        request.session['language'] = q
        if request.user.is_authenticated():
            user = User.objects.get(pk=request.user.id)
            profile = Profile.objects.get(user=user)
            profile.profile_language = q
            profile.save()
    return redirect('auction:index')


def languageFolderSelection(request):
    language = ''
    if 'language' in request.session:
        language = request.session['language']
    if language == 'fi':
        language = 'fi/'
    if language == 'sv':
        language = 'sv/'
    if language == 'en':
        language = ''
    return language


def setBaseTemplate(request):
    if request.user.is_authenticated():
        baseTemplate = "auction/base.html"
    else:
        baseTemplate = "auction/baseVisitor.html"
    return baseTemplate


def index (request):
    baseTemplate = setBaseTemplate(request)
    q = request.GET.get("q")
    if q:
        auction = Auction.objects.filter(auction_title__icontains=q, auction_status='Active').distinct().order_by('-id')
        return render(request, 'auction/'+languageFolderSelection(request) + 'index.html', {'objectL': auction, 'heading': 'Auction Results', 'baseTemplate': baseTemplate} )
    else:
        auction = Auction.objects.filter(auction_status='Active').order_by('-id')[:10]
        return render(request, 'auction/' + languageFolderSelection(request) + 'index.html', {'objectL': auction, 'heading': "Latest auctions", 'baseTemplate': baseTemplate})


def search(request):
    baseTemplate = setBaseTemplate(request)
    auction = Auction.objects.filter(auction_status='Active').order_by('-id')
    return render(request,  'auction/'+languageFolderSelection(request)+'index.html', {'objectL': auction, 'heading': "Auctions", 'baseTemplate': baseTemplate})


def searchBanned(request):
    if not request.user.is_superuser:
        return HttpResponse('You are not allowed to this function')
    baseTemplate = setBaseTemplate(request)
    auction = Auction.objects.filter(auction_status='Banned').order_by('-id')
    return render(request, 'auction/'+languageFolderSelection(request)+'index.html', {'objectL': auction, 'heading': "Banned Auctions", 'baseTemplate': baseTemplate})


@login_required(login_url='user:login')
def myAuction(request):
    baseTemplate = setBaseTemplate(request)
    auction = Auction.objects.filter(seller_name_id=request.user.pk, auction_status='Active').order_by('-id')[:10]
    return render(request, 'auction/'+languageFolderSelection(request)+'index.html', {'objectL': auction, 'heading': "My Auctions", 'baseTemplate': baseTemplate})


def auctionDetails(request, auction_id):
    q = request.GET.get("cur")
    currency = 'EUR'
    if q:
        currency = q
        request.session['project'] = currency
    else:
        if 'project' in request.session:
            currency = request.session['project']
    currency_value = exchangeCurrency(currency)
    auction = get_object_or_404(Auction, pk=auction_id, auction_status='Active')
    auction.bid_set.all()
    difference = auction.ending_date - timezone.now()
    seconds = difference.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    context = {
        'auction': auction,
        'hours': hours,
        'minutes': minutes,
        'baseTemplate': setBaseTemplate(request),
        'currency_list': currency_list,
        'currency': currency,
        'currency_value': currency_value}
    return render(request, 'auction/'+languageFolderSelection(request)+'details.html', context)


@login_required(login_url='user:login')
def createAuction(request):
        form = AuctionForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            context = {
                "form": form,
                'baseTemplate': "auction/base.html",
            }
            auction = form.save(commit=False)
            save_into_session(request, auction)
            return render(request, 'auction/'+languageFolderSelection(request)+'confirm_auction.html', context)
        context = {
           "form": form,
            'baseTemplate': "auction/base.html",
        }
        return render(request, 'auction/'+languageFolderSelection(request)+'auction.html', context)


def save_into_session(request, auction):
    request.session['auction_title'] = auction.auction_title
    request.session['description'] = auction.description
    request.session['starting_price'] = str(auction.starting_price)
    request.session['auction_duration_hours'] = auction.auction_duration_hours


@login_required(login_url='user:login')
def auctionConfirm(request):
        if request.method == 'POST':
            if (request.POST['confirm'] == 'True'):
                auction = get_from_session(request)
                auction.seller_name = request.user
                auction.starting_date = timezone.now()
                auction.ending_date = auction.starting_date + timedelta(hours=auction.auction_duration_hours)
                auction.token_edit = auction.starting_date.strftime('%Y%m%d%H%M%S') + get_random_string()
                auction.auction_revision = 1
                auction.save()
                subject = 'Auction is created'
                body = 'Auction with title "' + auction.auction_title + '" has been created'
                body += '\nto see the auction description follow the following link '
                body += '\n' + request.get_host() + '/auction/' + str(auction.id) + '/'
                body += '\nuse following link to edit auction details '
                body += '\n' + request.get_host() + '/auction/auction/non/edit/'+ auction.token_edit + '/'
                email = EmailMessage(subject, body, from_email='no-reply@yaas.com', to=['user@yaas.com'])
                email.send()
                return redirect('auction:index')
        return redirect('auction:index')


def get_from_session(request):
    auction = Auction()
    auction.auction_title = request.session['auction_title']
    auction.description = request.session['description']
    auction.auction_duration_hours = request.session['auction_duration_hours']
    auction.starting_price = Decimal(request.session['starting_price'])
    del request.session['auction_title']
    del request.session['description']
    del request.session['auction_duration_hours']
    del request.session['starting_price']
    return auction


class AuctionEditFormNonView(View):
    edit_form_class = EditAuctionForm
    def get(self, request, token_edit):
        template_name = 'auction/' + languageFolderSelection(request) + 'auction.html'
        form = self.edit_form_class(None)
        results = Auction.objects.filter(token_edit=token_edit).count()
        if results > 0:
            auction = Auction.objects.get(token_edit=token_edit)
            form.fields['description'].initial = auction.description
            return render(request, template_name, {'form': form, 'baseTemplate': setBaseTemplate(request)})
        return redirect('auction:index')
    def post(self, request, token_edit):
        template_name = 'auction/' + languageFolderSelection(request) + 'auction.html'
        form = self.edit_form_class(request.POST)
        if form.is_valid():
            data_auction = Auction.objects.get(token_edit=token_edit)
            data_auction.description = form.cleaned_data['description']
            data_auction.auction_revision = data_auction.auction_revision + 1
            data_auction.save()
            return redirect('auction:index')
        return render(request, template_name, {'form': form, 'baseTemplate': setBaseTemplate(request)})


class EditAuctionView(LoginRequiredMixin, View):
    login_url = 'user:login'
    redirect_field_name = 'redirect_to'
    edit_form_class = EditAuctionForm

    def get(self, request, pk):
        template_name = 'auction/' + languageFolderSelection(request) + 'auction.html'
        form = self.edit_form_class(None)
        results = Auction.objects.filter(pk=pk).count()
        if results > 0:
            auction = Auction.objects.get(pk=pk)
            form.fields['description'].initial = auction.description
            if request.user != auction.seller_name:
                return HttpResponse('You are not allowed to perform this action')
            return render(request, template_name, {'form': form, 'baseTemplate': "auction/base.html"})
        return redirect('auction:index')

    def post(self, request, pk):
        template_name = 'auction/' + languageFolderSelection(request) + 'auction.html'
        form = self.edit_form_class(request.POST)
        if form.is_valid():
            data_auction = Auction.objects.get(pk=pk)
            data_auction.description = form.cleaned_data['description']
            data_auction.auction_revision = data_auction.auction_revision + 1
            data_auction.save()
            return redirect('auction:index')
        return render(request, template_name, {'form': form, 'baseTemplate': "auction/baseVisitor.html"})


def banAuction(request, pk):
    if request.user.is_superuser:
        auction = Auction.objects.get(id=pk)
        auction.auction_status = "Banned"
        auction.save()
        bannedEmailSending(pk)
    else:
        return HttpResponse("HTTP 403 Forbidden : You are not authorized to ban", status=403)
    return redirect('auction:index')


def bannedEmailSending(auction_id):
    auction = Auction.objects.get(pk=auction_id)
    to = [auction.seller_name.email]
    count = Bid.objects.filter(auction=auction).count()
    if count > 0:
        bids = Bid.objects.filter(auction=auction)
        for b in bids:
            to.append(b.bidder_name.email)

    subject = 'Admin has banned the auction'
    body = 'Auction with title "' + auction.auction_title + '" has been banned by Admin'
    body += '\nContact with authority for more information.'
    email = EmailMessage(subject, body, from_email='no-reply@yaas.com', to=to)
    email.send()



def unbanAuction(request, pk):
    if request.user.is_superuser:
        auction = Auction.objects.get(id=pk, auction_status='Banned')
        auction.auction_status = "Active"
        auction_delta = auction.ending_date - timezone.now()
        expiry_check = auction_delta.total_seconds()
        if (expiry_check < 0):
            auction.auction_status = "Due"
        auction.save()
    else:
        return HttpResponse("HTTP 403 Forbidden : You are not authorized to perform this function", status=403)
    return redirect('auction:index')


class BidFormFormView(LoginRequiredMixin, View):
    login_url = 'user:login'
    redirect_field_name = 'redirect_to'
    class_form = BiddingForm

    def get(self, request, auction_id):
        template_name = 'auction/' + languageFolderSelection(request) + 'bid.html'
        form = self.class_form(None)
        auction = get_object_or_404(Auction, pk=auction_id)
        return render(request, template_name, {'form': form, 'auction': auction})

    def post(self, request, auction_id):
        template_name = 'auction/' + languageFolderSelection(request) + 'bid.html'
        auction = Auction.objects.get(pk=auction_id)
        form = self.class_form(request.POST)
        print(form.errors)
        if form.is_valid():
            bid = form.save(commit=False)
            revision_bid = int(request.POST['auction_revision'])
            bidding_value = form.cleaned_data['bidding_value']

            auction_delta = auction.ending_date - timezone.now()
            expiry_check = auction_delta.total_seconds()
            hours = int(expiry_check // 3600)
            minutes = int((expiry_check % 3600) // 60)
            error_message = bid_verifying(request.user, auction, revision_bid, bidding_value)
            if error_message != '':
                return render(request, template_name,
                              {'form': form, 'auction': auction, 'error_message': error_message})
            bid.bidding_value = bidding_value
            bid.auction = auction
            bid.bidder_name = request.user
            count = Bid.objects.filter(auction=auction, bidder_name=request.user).count()
            if(count>0):
                bid2 = Bid.objects.get(auction=auction, bidder_name=request.user)
                bid2.bidding_value= bidding_value
                bid2.save()
            else:
                bid.save()
            # Soft deadlines
            if(hours==0 and minutes<5):
                auction.ending_date = auction.ending_date + timedelta(minutes=5)

            auction.bidding_price = bidding_value
            auction.winner_id = request.user.pk
            auction.save()
            # Send email
            bidEmailSening(auction_id)
            return redirect('auction:index')
        return render(request, template_name, {'form': form, 'auction': auction})


def bid_verifying(user, auction, revision_bid, bidding_value):
    if (revision_bid != auction.auction_revision):
        return 'Seller has updated bid description, please read the description before placing your bid.'
    if (auction.bidding_price):
        if (bidding_value <= auction.bidding_price):
            return 'Your bidding price is lower than current price.'
    if (bidding_value <= auction.starting_price):
        return 'Bidding price should be higher than current price.'
    if (auction.winner_id == user.pk):
        return 'You are the highest bidder'
    if (auction.seller_name.pk == user.pk):
        return 'You are not allowed to bid in your own auction.'
    auction_delta = auction.ending_date - timezone.now()
    expiry_check = auction_delta.total_seconds()
    if (expiry_check < 0):
        return 'Auction Expired!'
    if (auction.auction_status != 'Active'):
        return 'Not Available.'
    return ''


def bidEmailSening(auction_id):
    auction = Auction.objects.get(pk=auction_id)
    bids = Bid.objects.filter(auction=auction)
    to = [auction.seller_name.email]
    newBidder = ''
    for b in bids:
        to.append(b.bidder_name.email)
        if b.bidder_name.id == auction.winner_id:
            newBidder = b.bidder_name.username

    subject = 'New bid'
    body = 'Auction with title "' + auction.auction_title + '" has a new bid.'
    body += '\nNew bidding price is = ' + str(auction.bidding_price) + ''
    body += '\nBidder name is = ' + newBidder + ''
    email = EmailMessage(subject, body, from_email='no-reply@yaas.com', to=to)
    email.send()


def resolveEmailSending(auction_id):
    auction = Auction.objects.get(pk=auction_id)
    count = Bid.objects.filter(auction=auction).count()
    if count > 0:
        bids = Bid.objects.filter(auction=auction)
        to = [auction.seller_name.email]
        winnerName = User.objects.get(pk=auction.winner_id).username
        for b in bids:
            to.append(b.bidder_name.email)
        subject = 'Adjudicated auction'
        body = 'Auction with title "' + auction.auction_title + '" has been Adjudicated'
        body += '\nWinning bidding price is = ' + str(auction.bidding_price) + ''
        body += '\nThe winner is = ' + winnerName + ''
        email = EmailMessage(subject, body, from_email='no-reply@yaas.com', to=to)
        email.send()
    else:
        to = [auction.seller_name.email]
        subject = 'Adjudicated auction'
        body = 'Auction with title "' + auction.auction_title + '" has been Adjudicated'
        body += '\nAuction has expired without any bid.'
        email = EmailMessage(subject, body, from_email='no-reply@yaas.com', to=to)
        email.send()



class Threading(object):

    def __init__(self):

        thread = threading.Thread(target=self.put_due, args=())
        thread.daemon = True
        thread.start()

        thread2 = threading.Thread(target=self.auctionResolve, args=())
        thread2.daemon = True
        thread2.start()

        thread3 = threading.Thread(target=self.exchangeCurrencyApi, args=())
        thread3.daemon = True
        thread3.start()

    def put_due(self):
        while True:
            auctions = Auction.objects.filter(auction_status='Active', ending_date__lt=timezone.now())
            for auction in auctions:
                auction.auction_status = 'Due'
                auction.save()
            time.sleep(60)

    def auctionResolve(self):
        while True:
            auctions = Auction.objects.filter(auction_status='Due', ending_date__lt=timezone.now())
            for auction in auctions:
                auction.auction_status = 'Adjudicated'
                auction.save()
                resolveEmailSending(auction.id)
            time.sleep(300)

    def exchangeCurrencyApi(self):
        while True:
            apiUrl = 'http://api.fixer.io/latest'
            temp = requests.get(apiUrl)
            json_data = temp.json()
            for item in currency_list:
                currency = item.get('value')
                if currency != 'EUR':
                    currency_value = json_data['rates'][currency]
                    if SetCurrency.objects.filter(currency=currency).exists():
                        cur = SetCurrency.objects.get(currency=currency)
                        cur.value = currency_value
                        cur.save()
                    else:
                        cur = SetCurrency()
                        cur.currency = currency
                        cur.value = currency_value
                        cur.save()
            time.sleep(600)


Task = Threading()


















