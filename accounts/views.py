from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    if request.method=="POST":
        u=request.POST.get("username","").strip()
        p=request.POST.get("password","")
        user=authenticate(request, username=u, password=p)
        if user:
            login(request,user)
            return redirect("home")
        messages.error(request,"Nieprawidłowy login lub hasło.")
    return render(request,"accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    return render(request,"accounts/profile.html")
