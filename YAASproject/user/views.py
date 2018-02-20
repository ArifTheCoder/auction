from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from auction.models import Profile
from django.views.generic import View
from .forms import UserForm, EditUserForm, LoginForm
from auction.views import languageFolderSelection
from django.contrib.auth.decorators import login_required


# Create new user.
class UserFormView(View):
    class_form = UserForm

    def get(self, request):
        template_name = 'auction/' + languageFolderSelection(request) + 'registration-form.html'
        form = self.class_form(None)
        return render(request, template_name, {'form': form})

    def post(self, request):
        form = self.class_form(request.POST)
        template_name = 'auction/' + languageFolderSelection(request) + 'registration-form.html'
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            profile = Profile()
            profile.profile_language = 'en'
            profile.user = user
            profile.save()
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    request.session['profile_language'] = User.objects.get(pk=user.id).profile.profile_language
                    return redirect('auction:index')

        return render(request, template_name, {'form': form})


class EditUserFormView(LoginRequiredMixin, View):
    login_url = 'user:login'
    redirect_field_name = 'redirect_to'
    class_form = EditUserForm

    def get(self, request):
        template_name = 'auction/' + languageFolderSelection(request) + 'edit-registration.html'
        form = self.class_form(None)
        form.fields['email'].initial = request.user.email
        return render(request, template_name, {'form': form})

    def post(self, request):
        form = self.class_form(request.POST)
        template_name = 'auction/' + languageFolderSelection(request) + 'edit-registration.html'

        if form.is_valid():
            db_user = User.objects.get(pk=request.user.id)
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            db_user.email = user.email
            if password == form.cleaned_data['confirm_password']:
                db_user.set_password(password)
                db_user.save()
                logout(request)
                return redirect('user:login')
            return render(request, template_name, {'form': form, 'error_message': "Both passwords should match"})
        return render(request, template_name, {'form': form})


class LoginFormView(View):
    class_form = LoginForm

    def get(self, request):
        template_name = 'auction/' + languageFolderSelection(request) + 'login.html'
        form = self.class_form(None)
        return render(request, template_name, {'form': form})

    def post(self, request):
        template_name = 'auction/' + languageFolderSelection(request) + 'login.html'
        form = self.class_form(request.POST)
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:
                login(request, user)
                try:
                    profile_language = User.objects.get(pk=user.id).profile.profile_language
                except:
                    profile = Profile()
                    profile.profile_language = 'en'
                    profile.user = User.objects.get(pk=user.id)
                    profile.save()
                request.session['profile_language'] = User.objects.get(pk=user.id).profile.profile_language
                q = request.POST.get('next')
                if q:
                    return redirect(q)
                return redirect('auction:index')

        return render(request, template_name, {'form': form, 'error_message': "Invalid credentials"})


@login_required(login_url='user:login')
def userLogout(request):
    logout(request)
    return redirect('auction:index')







