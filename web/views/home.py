from django.shortcuts import render


def home_index(request):
    """首页"""
    return render(request, 'index.html')