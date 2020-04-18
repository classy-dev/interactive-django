from django.shortcuts import render, redirect
from account.forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

@login_required
def special(request):
    return HttpResponse("You are logged in !")

def index(request):
    return render(request, 'account/index.html', {})

@login_required
def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('account:login'))

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('backtest:index')
            else:
                return HttpResponse("Your account was inactive.")
        else:          
            return render(request, 'account/login.html', {
                'error': "Username and Password is incorrect"
            })
    else:
        if request.user.is_authenticated == True:
            return redirect('backtest:index')
        return render(request, 'account/login.html', {})

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return render(request, 'account/signup.html',{
                'error': "That username exists"
            })
        else:
            user = User.objects.create_user(username=username, password=password)
            return render(request, 'account/login.html',)
    return render(request, 'account/signup.html',)

    

