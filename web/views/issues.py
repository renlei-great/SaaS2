from django.http import JsonResponse
from django.shortcuts import render, redirect

from web.forms.issues import IssuesForm


def issues(request, pro_id):
    """问题首页"""
    form = IssuesForm()
    a = 1

    return render(request, 'issues.html', {'form': form})