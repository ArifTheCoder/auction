from django.http import HttpResponse
from django.shortcuts import render
from auction.models import Profile, Auction, Bid
from django.contrib.auth.models import User
from YAASproject import DBdata


def index(request):
    return render(request, 'YAASproject/index.html')


# generate data in database
def db_generator(request):
    Profile.objects.all().delete()
    Bid.objects.all().delete()
    Auction.objects.all().delete()
    User.objects.all().delete()
    su = User(username='admin')
    su.set_password('admin1234')
    su.is_superuser = True
    su.is_staff = True
    su.save()
    profile = Profile()
    profile.profile_language = 'en'
    profile.user = User.objects.get(pk=su.id)
    profile.save()
    db_data = DBdata.DBdataGenerator()
    db_data.data_generate()
    return HttpResponse('Successfully created!')


def generate_test_db():
    Profile.objects.all().delete()
    Bid.objects.all().delete()
    Auction.objects.all().delete()
    User.objects.all().delete()
    su = User(username='admin')
    su.set_password('admin1234')
    su.is_superuser = True
    su.is_staff = True
    su.save()
    profile = Profile()
    profile.profile_language = 'en'
    profile.user = User.objects.get(pk=su.id)
    profile.save()
    db_data = DBdata.DBdataGenerator()
    db_data.data_generate()
