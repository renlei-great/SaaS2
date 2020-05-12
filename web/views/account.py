from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection

from utils.tencent.sms import send_sms_single
from web.forms.account import RegisterForm, SendSmSFoem, LoginSmsForm, CaptchaForm
from web.models import UserInfo


def login_sms(request):
    """短信登录"""
    if request.method == 'GET':
        login_form = LoginSmsForm()
        capt = CaptchaForm()

        return render(request, 'login.html', {'form': login_form, 'capt': capt})
        # return render(request, 'login.html', {'form': login_form})

    if request.method == 'POST':
        """表单提交"""
        login_form = LoginSmsForm(request.POST)
        capt = CaptchaForm(request.POST)

        if login_form.is_valid() and capt.is_valid():
            user_object = login_form.cleaned_data['mobile_phpne']
            mobile_phpne = user_object.mobile_phpne

            # 删除redis中的记录
            conn = get_redis_connection()
            conn.delete(mobile_phpne)

            return JsonResponse({'status': True, 'data': '/index'})

        for key, val in login_form.errors.items():
            """动态结合两个表单的错误信息"""
            capt.errors[key] = val

        return JsonResponse({'status': False, 'error': capt.errors})
        # return render(request, 'user/login.html', {'form': login_form, 'capt': capt})


def register(request):
    """用户注册"""
    if request.method == 'GET':
        # 显示
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    elif request.method == 'POST':
        # 处理提交
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'status': False, 'error': form.errors})
        user = form.save()
        conn = get_redis_connection()
        conn.delete(user.mobile_phpne)
        return JsonResponse({'status': True, 'data': 'loginsms'})


def send_sms(request):
    """发送验证码"""
    form = SendSmSFoem(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})
