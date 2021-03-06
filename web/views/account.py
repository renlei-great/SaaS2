import uuid
import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from web.forms.account import RegisterForm, SendSmSFoem, LoginSmsForm, CaptchaForm, LoginForm
from web.models import UserInfo, PricePolicy, Transaction


def login(request):
    """密码登录"""
    if request.method == 'GET':
        login_form = LoginForm()
        captcha = CaptchaForm()

        return render(request, 'login.html', {'form': login_form, 'capt': captcha})

    if request.method == 'POST':
        """表单提交"""
        login_form = LoginForm(request.POST)
        capt = CaptchaForm(request.POST)

        if not capt.is_valid():
            return JsonResponse({'status': False, 'error': capt.errors})

        if not login_form.is_valid():
            return JsonResponse({'status': False, 'error': login_form.errors})

        # 在forms中直接写了返回用户模型对象
        user_object = login_form.cleaned_data['mobile_phpne']

        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        url_path = request.GET.get('url_path')

        # 检测URL来前访问的地址
        if url_path:
            return JsonResponse({'status': True, 'data': url_path})
        return JsonResponse({'status': True, 'data': '/web/index'})


def login_sms(request):
    """短信登录"""
    if request.method == 'GET':
        login_form = LoginSmsForm()

        return render(request, 'loginsms.html', {'form': login_form})
        # return render(request, 'login.html', {'form': login_form})

    if request.method == 'POST':
        """表单提交"""
        login_form = LoginSmsForm(request.POST)

        if login_form.is_valid():
            user_object = login_form.cleaned_data['mobile_phpne']
            mobile_phpne = user_object.mobile_phpne

            # 删除redis中的记录
            conn = get_redis_connection()
            conn.delete(mobile_phpne)

            request.session['user_id'] = user_object.id
            request.session.set_expiry(60 * 60 * 24 * 14)

            return JsonResponse({'status': True, 'data': '/web/index'})

        return JsonResponse({'status': False, 'error': login_form.errors})


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

        # 添加用户交易记录
        price_policy = PricePolicy.objects.filter(category=1, title="个人免费版").first()
        Transaction.objects.create(
            status=2,
            order_id=str(uuid.uuid4()),
            user=user,
            price_policy=price_policy,
            count=0,
            actual_price=0,
            start_time=datetime.datetime.now()
        )

        conn = get_redis_connection()
        conn.delete(user.mobile_phpne)

        request.session['user_id'] = user.id
        request.session.set_expiry(60*60*24*14)

        return JsonResponse({'status': True, 'data': 'loginsms'})


def send_sms(request):
    """发送验证码"""
    form = SendSmSFoem(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def exit(request):
    """退出登录"""
    request.session.flush()
    return redirect('web:index')
