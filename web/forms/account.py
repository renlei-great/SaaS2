
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django_redis import get_redis_connection
import bcrypt
from captcha.fields import CaptchaField

from utils.tencent.sms import send_sms_single
from web.forms.bootstrap import BootsTrap
from web.models import UserInfo
# 自定义表单的正则匹配
from django.core.validators import RegexValidator
from saas_29.settings import SMS_TEMPLATE


class CaptchaForm(forms.Form):
    captcha = CaptchaField()


class LoginSmsForm(BootsTrap, forms.Form):
    """用户短信登录表单"""
    mobile_phpne = forms.CharField(label='手机号', validators=[RegexValidator(r'^1([3|4|5|6|7|8|9])\d{9}', '手机格式错误')])
    code = forms.CharField(label="验证码")

    def clean_mobile_phpne(self):
        mobile = self.cleaned_data['mobile_phpne']
        user_object = UserInfo.objects.filter(mobile_phpne=mobile).first()
        if not user_object:
            raise ValidationError('手机号未注册++')

        return user_object

    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            user_object = self.cleaned_data['mobile_phpne']
        except KeyError:
            raise ValidationError('')

        # 从redis中取数据
        conn = get_redis_connection()
        code_redis = conn.get(user_object.mobile_phpne)
        try:
            code_redis = code_redis.decode()
            if code_redis != code:
                pass
                raise ValidationError('验证码错误')
            pass
            return code
        except AttributeError:
            raise ValidationError('请先获取验证码')


class RegisterForm(BootsTrap, forms.ModelForm):
    """注册表单"""
    email = forms.EmailField(label='邮箱')
    # 自定义表单的正则匹配
    mobile_phpne = forms.CharField(label="手机", required=True, validators=[RegexValidator(r'^1([3|4|5|6|7|8|9])\d{9}', '手机格式错误--'),])
    # 自定义输入框的格式
    password = forms.CharField(label="密码", required=True, min_length=3, max_length=32, widget=forms.PasswordInput())

    password1 = forms.CharField(label="再次输入密码", min_length=3, max_length=32, required=True, widget=forms.PasswordInput())
    code = forms.CharField(label="验证码")

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'password1','mobile_phpne',  'code']

    def clean_password(self):
        # 对用户密码加密
        password = self.cleaned_data['password']
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return password

    def clean_email(self):
        """验证邮箱是否被注册过"""
        email = self.cleaned_data['email']
        qs = UserInfo.objects.filter(email=email)
        if qs:
            raise ValidationError('邮箱已被注册')
        return email

    def clean_mobile_phpne(self):
        mobile_phpne = self.cleaned_data['mobile_phpne']

        # 查看手机号是否被注册
        qy = UserInfo.objects.filter(mobile_phpne=mobile_phpne)
        if qy:
            raise ValidationError('该手机号已注册')

        return mobile_phpne

    def clean_code(self):
        # 获取数据
        a = self
        try:
            code = self.cleaned_data['code']
            mobile_phpne = self.cleaned_data['mobile_phpne']
        except KeyError:
            raise ValidationError('')

        # 向redis数据库中取出验证码
        conn = get_redis_connection('default')
        redis_code = conn.get(mobile_phpne)

        # 校验数据
        try:
            if code != redis_code.decode():
                raise ValidationError('验证码错误')
        except AttributeError:
            raise ValidationError('请先获取验证码')

        return code

    def clean(self):
        password = self.cleaned_data.get('password', None)
        password1 = self.cleaned_data.get('password1', None)
        if password is None or password1 is None:
            self.add_error('password1', '请输入密码')
        elif not bcrypt.checkpw(password1.encode(), password):
            self.add_error('password1', '两次密码不一致')

        return self.cleaned_data


class SendSmSFoem(forms.Form):
    """发送短信表单"""
    mobile_phpne = forms.CharField(label="手机", min_length=11, max_length=11, validators=[RegexValidator(r'^1([3|4|5|6|7|8|9])\d{9}$', '手机格式错误')])

    def __init__(self, request,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phpne(self):

        mobile_phpne = self.cleaned_data['mobile_phpne']
        tpl = self.request.GET.get('tpl')

        if tpl == 'register':
            # 查看手机号是否被注册
            qy = UserInfo.objects.filter(mobile_phpne=mobile_phpne)
            if qy:
                raise ValidationError('该手机号已注册')
        elif tpl == 'login':
            # 查看手机号是否被注册
            qy = UserInfo.objects.filter(mobile_phpne=mobile_phpne)
            if not qy:
                raise ValidationError('该手机号未注册--')

        # 查看短信模板是否正确

        if not SMS_TEMPLATE.get(tpl):
            raise ValidationError('请求格式错误')

        # 发送短信验证码
        res = send_sms_single(tpl, mobile_phpne)
        if res['result'] != 0:
            raise ValidationError('短信发送失败：{}'.format(res['errmsg']))

        return mobile_phpne



