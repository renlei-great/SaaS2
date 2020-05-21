import datetime

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from web.models import UserInfo, Transaction
from saas_29.settings import BLACK_REGEX_URL_LEST


class Tracer:
    # 封装自定义参数
    user = None
    price_policy = None


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """如果用户已登录，则request中赋值"""
        request.tracer = Tracer()
        user_id = request.session.get('user_id')
        user_object = UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_object

        # 用户登录验证，导入白名单
        if request.path_info in BLACK_REGEX_URL_LEST:
            if request.tracer.user:
                # 用户已经登录
                # 获取用户的权限
                obj_trans = Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id')

                # 将本用户的价格策略赋给request对象
                now_date = datetime.datetime.now()
                s = obj_trans[0].start_time
                if obj_trans[0].over_time and obj_trans[0].over_time > now_date:
                    request.tracer.price_policy = obj_trans[0].price_policy
                else:
                    obj_tran = obj_trans.order_by('id').first()
                    request.tracer.price_policy = obj_tran.price_policy

            else:
                return redirect('web:login')

