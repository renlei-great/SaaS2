import datetime
import re

from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.utils.deprecation import MiddlewareMixin

from web.models import UserInfo, Transaction, ProjectUser, Project
from saas_29.settings import BLACK_REGEX_URL_LEST


class Tracer:
    # 封装自定义参数
    user = None
    price_policy = None
    project = None


class AuthMiddleware(MiddlewareMixin):
    """自定义中间件"""
    def process_request(self, request):
        """如果用户已登录，则request中赋值"""
        request.tracer = Tracer()
        user_id = request.session.get('user_id')
        user_object = UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_object
        url_path = request.get_full_path()  # 获取当前请求URL的完整路径
        # 取出url
        try:
            url = re.search(r'(/web/\w+)/', request.path_info + '/').group(1)
        except AttributeError:
            url = request.path_info
        # 用户登录验证，导入黑名单
        if url in BLACK_REGEX_URL_LEST:
            if request.tracer.user:
                # 用户已经登录
                # 获取用户的权限
                obj_trans = Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id')

                # 将本用户的价格策略赋给request对象
                now_date = datetime.datetime.now()
                # s = obj_trans[0].start_time
                if obj_trans[0].over_time and obj_trans[0].over_time > now_date:
                    request.tracer.price_policy = obj_trans[0].price_policy
                else:
                    obj_tran = obj_trans.order_by('id').first()
                    request.tracer.price_policy = obj_tran.price_policy
            else:
                return redirect(f'/web/login?url_path={url_path}')

    def process_view(self, request, view, args, kwargs):
        # 如果url是manage开头，那么就进行判断项目id是不是他自己的
        if not request.path_info.startswith('/web/manage'):
            return

        pro_id = kwargs.get('pro_id', None)
        if not pro_id:
            redirect('web:project')

        user = request.tracer.user
        # 查看是否有此用户的此项目
        project = Project.objects.filter(id=int(pro_id), creator=user).first()
        user_project = ''
        if not project:
            user_project = ProjectUser.objects.filter(project=pro_id, user=user).first()

        # 判断是否有此项目，是不是该用户的
        if not any([project, user_project]):
            redirect('web:project')

        request.tracer.project = user_project.project if user_project else project


