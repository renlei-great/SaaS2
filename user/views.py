from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from utils.tencent.sms import send_sms_single


# Create your views here.
def send_sms(request):
    """发送验证码"""
    tpl = request.POST.get('tpl')
    mobile = request.POST.get('mobile')

    qy = UserInfo.objects.filter(mobile_phpne=mobile)
    if qy:
        return JsonResponse({'filed': 'mobile_phpne', 'result': '2', 'errmsg': '该手机号已注册'})

    try:
        mobile = int(mobile)
        res = send_sms_single(tpl, mobile)
        res['errmsg'] = '发送成功'
        res['filed'] = 'code'
        return JsonResponse(res)
    except:
        return JsonResponse({'filed': 'mobile_phpne', 'result': '2', 'errmsg': '发送失败'})


from django import forms
from user.models import UserInfo
# 自定义表单的正则匹配
from django.core.validators import RegexValidator


class RegisterForm(forms.ModelForm):
    # 自定义表单的正则匹配
    mobile_phpne = forms.CharField(label="手机", validators=[RegexValidator(r'^1[3|4|5|6|7|8|9]\d[9]', '手机格式错误'),])
    # 自定义输入框的格式
    password = forms.CharField(label="密码", widget=forms.PasswordInput())

    password1 = forms.CharField(label="再次输入密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码")

    def clean(self):
        password = self.data.get['password', 1]
        password1 = self.data.get['password1', 2]
        if password != password1:
            return HttpResponse('两次密码不一致')
        return password

    def clean_mobile_phpne(self):
        mobile_phpne = self.data.get['mobile_phpne']
        user = UserInfo()
        qy = user.objects.filter(mobile_phpne=mobile_phpne)
        if qy:
            raise forms.ValidationError('该手机号已注册')
        return mobile_phpne

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'password', 'password1','mobile_phpne',  'code']

    def __init__(self, *args, **kwargs):
        """重写给每个字段动态添加属性"""
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = '请输入{}'.format(filed.label)


def register(request):
    if request.method == 'GET':
        eh = request.POST.get('hh')
        print(eh, 'sss')
        form = RegisterForm()
        return render(request, 'user/register.html', {'form':form})

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        # 获取数据
        username = form.data['username']
        email = form.data['email']
        password = form.data['password']
        password1 = form.data['password1']
        mobile = form.data['mobile_phpne']
        code = form.data['code']

        # 校验数据是否有空值
        if not all([username, email, password, password1, mobile, code]):
            return JsonResponse({'filed': 'code', 'errmsg': '请填写完整'})
        # 向redis数据库中取出验证码
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        redis_code = conn.get(mobile)

        # 校验数据
        try:
            if code != redis_code.decode():
                return JsonResponse({'filed': 'code', 'errmsg': '验证码错误'})
        except AttributeError:
            return JsonResponse({'filed': 'code', 'errmsg': '请先获取验证码'})

        if password != password1:
            return JsonResponse({'filed': 'password1', 'errmsg': '两次密码不一致'})



        # 向mysql数据库添加数据
        user = UserInfo(username=username, email=email, password=password, mobile_phpne=mobile)
        user.save()
        conn.delete(mobile)
        return HttpResponse('注册成功')


def login(request):
    return send_sms(request)