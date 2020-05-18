from django.shortcuts import render
from django.http import JsonResponse
from django_redis import get_redis_connection
# 自定义表单的正则匹配
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from captcha.fields import CaptchaField

from utils.tencent.sms import send_sms_single
from user_app.user.models import UserInfo


# Create your views here.
def send_sms(request):
    """发送验证码"""
    tpl = request.GET.get('tpl')
    mobile = request.GET.get('mobile_phpne')

    qy = UserInfo.objects.filter(mobile_phpne=mobile)
    if tpl == 'register':
        if qy:
            return JsonResponse({'filed': 'mobile_phpne', 'result': '2', 'errmsg': '该手机号已注册'})
    elif tpl == 'login':
        if not qy:
            return JsonResponse({'filed': 'mobile_phpne', 'result': '2', 'errmsg': '该手机号未注册'})

    try:
        mobile = int(mobile)
        res = send_sms_single(tpl, mobile)
        res['errmsg'] = '发送成功'
        res['filed'] = 'code'
        return JsonResponse(res)
    except TypeError:
        return JsonResponse({'filed': 'code', 'result': '2', 'errmsg': '发送失败'})


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='邮箱')
    # 自定义表单的正则匹配
    mobile_phpne = forms.CharField(label="手机", validators=[RegexValidator(r'^1([3|4|5|6|7|8|9])\d{9}', '手机格式错误'),])
    # 自定义输入框的格式
    password = forms.CharField(label="密码", widget=forms.PasswordInput())

    password1 = forms.CharField(label="再次输入密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码")

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'password1', 'mobile_phpne',  'code']

    def __init__(self, *args, **kwargs):
        """重写给每个字段动态添加属性"""
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)

    def clean_email(self):
        """验证邮箱是否被注册过"""
        email = self.cleaned_data['email']
        qs = UserInfo.objects.filter(email=email)
        if qs:
            raise ValidationError('邮箱已被注册')
        return email

    def clean_code(self):
        # 获取数据
        print('sksks嗯哼')
        print(self.cleaned_data)
        code = self.cleaned_data['code']

        mobile_phpne = self.cleaned_data['mobile_phpne']
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
        if password != password1:
            self.add_error('password1', '两次密码不一致')

        return self.cleaned_data


def register(request):
    """注册"""
    if request.method == 'GET':
        eh = request.POST.get('hh')
        print(eh, 'sss')
        form = RegisterForm()
        return render(request, 'user/register.html', {'form':form})

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        error = form.errors
        if not form.is_valid():
            return JsonResponse({'status': False, 'error': form.errors})
        # 获取数据
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        mobile = form.cleaned_data['mobile_phpne']
        # ---------

        # 向mysql数据库添加数据
        user = UserInfo(username=username, email=email, password=password, mobile_phpne=mobile)
        user.save()
        conn = get_redis_connection()
        conn.delete(mobile)
        return JsonResponse({'status': True})
        # except:
        #     return JsonResponse({'status': False, 'error': '注册失败'})


class LoginForm(forms.Form):
    """用户短信登录表单"""
    mobile_phpne = forms.CharField(label='手机号', validators=[RegexValidator(r'^1([3|4|5|6|7|8|9])\d{9}', '手机格式错误')])
    code = forms.CharField(label="验证码")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile_phpne']
        qs = UserInfo.objects.filter(mobile_phpne=mobile)
        if not qs:
            raise ValidationError('手机号未注册')

        return mobile

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile = self.cleaned_data['mobile_phpne']
        conn = get_redis_connection()
        code_redis = conn.get(mobile)
        if code_redis.decode() != code:
            raise ValidationError('验证码错误-->')

        return code

class CaptchaForm(forms.Form):
    captcha = CaptchaField()


def login(request):
    if request.method == 'GET':
        login_form = LoginForm()
        capt = CaptchaForm()

        return render(request, 'user/login.html', {'form': login_form, 'capt': capt})
    if request.method == 'POST':
        """表单提交"""
        login_form = LoginForm(request.POST)
        capt = CaptchaForm(request.POST)

        if login_form.is_valid() and capt.is_valid():
            conn = get_redis_connection()
            conn.delete(login_form.cleaned_data['mobile_phpne'])
            return JsonResponse({'status': True})

        for key, val in login_form.errors.items():
            """动态结合两个表单的错误信息"""
            capt.errors[key] = val

        return JsonResponse({'status': False, 'error': capt.errors})