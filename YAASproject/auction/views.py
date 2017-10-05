from .models import Auction
from django.shortcuts import render, get_object_or_404

def index(request):
    allAuctions = Auction.objects.all()
    context = {'allAuctions': allAuctions}
    return render(request, 'auction/index.html', context,)


def detail(request, auctionID):
    auction = get_object_or_404(Auction, pk=auctionID)
    return render(request, 'auction/detail.html', {'auction': auction})


def search_form(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        searched_auction = Auction.objects.filter(auctionTitle__icontains=q)
        return render(request, 'auction/search_result.html',
                      {'searched_auction': searched_auction, 'query': q})
    else:
        return render(request, 'auction/index.html', {'error_msg': 'Enter a valid value'})

