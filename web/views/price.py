import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, reverse

from web.models import PricePolicy, Transaction


def price_show(request):
    """价格显示"""
    # 查询出来所有的套餐
    price_list = PricePolicy.objects.all()
    return render(request, 'price.html', {'policy_list': price_list})


def payment(request, policy_id):
    """支付页面"""
    # 获取需要的数据
    # 用户的订单
    user_transa = Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id').first()
    # user_transa = request.tracer.price_policy
    # 用户要购买的套餐数量
    number = request.GET.get('number', 'not')

    #　判断前段传来的数据是否合法
    if number.isdecimal():
        if int(number) < 1:
            return redirect(reverse('web:price_show'))
        number = int(number)

    # 查询用户要购买的套餐
    policy_object = PricePolicy.objects.get(id=policy_id)

    # 求出用户购买的套餐需要的原价
    origin_price = number * policy_object.price

    # 查看用户是否有购买套餐
    if user_transa.actual_price == 0:
        # 不需要考虑用户以前的套餐
        # 为前端返回数据
        context = {
            'origin_price': origin_price,
            'policy_object': policy_object,
            'number': number,
            'balance': 0,
            'total_price': origin_price,
        }
        return render(request, 'payment.html', context)

    # 考虑用户以前的套餐
    day_price = user_transa.price_policy.price / 365  # 求出一天的价钱

    # 求出用户可以抵扣多少钱
    total_timedelta = user_transa.over_time - user_transa.start_time
    balance_timedelta = user_transa.over_time - datetime.datetime.now()

    if balance_timedelta.days <= 0:
        return redirect(reverse('web:price_show'))

    if total_timedelta.days == balance_timedelta.days:
        balance = 364 * day_price
    else:
        balance = balance_timedelta.days * day_price

    # 求出实际支付的价格
    total_price = origin_price - balance

    # 为前端返回数据
    context = {
        'origin_price': origin_price,
        'policy_object': policy_object,
        'number': number,
        'balance': balance,
        'total_price': total_price,
    }

    return render(request, 'payment.html', context)