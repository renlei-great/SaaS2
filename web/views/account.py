from django.shortcuts import render
from web.forms.account import RegisterForm


def register(request):
    form = RegisterForm()
    return render(request, 'register.html', {'form':form})