from django.utils.deprecation import MiddlewareMixin
from user_app.user.models import UserInfo


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """如果用户已登录，则request中赋值"""
        user_id = request.session.get('user_id')
        user_object = UserInfo.objects.filter(id=user_id)
        if user_object:
            request.tracer = user_object[0]