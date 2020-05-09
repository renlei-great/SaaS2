from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from utils.tencent.sms import send_sms_single
from web.forms.account import RegisterForm, SendSmSFoem
from web.models import UserInfo


def register(request):
    form = RegisterForm()
    form.is_valid()
    return render(request, 'register.html', {'form':form})


def send_sms(request):
    """发送验证码"""
    form = SendSmSFoem(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})