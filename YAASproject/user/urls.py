from django.conf.urls import url
from . import views


app_name = 'user'

urlpatterns = [
    url(r'^register/$', views.UserFormView.as_view(), name='register-form'),
    url(r'^editprofile/$', views.EditUserFormView.as_view(), name='edit-profile'),
    url(r'^login/$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout/$', views.userLogout, name='logout'),
]

